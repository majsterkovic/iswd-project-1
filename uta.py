import pandas as pd
import pulp
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict

plt.style.use("ggplot")


def solve_lp_problem(
    df: pd.DataFrame,
    preferential_info: List[tuple],
    indiff_info: List[tuple],
    verbose=True,
    gms=False,
):
    criteria = df.columns.tolist()
    all_alternatives = df.index.tolist()

    pulp.LpSolverDefault.msg = 0
    problem = pulp.LpProblem("UTA", pulp.LpMaximize)
    print("Kryteria:", criteria)

    # VARIABLES
    u_vars = {}
    for alternative in all_alternatives:
        for criterion in criteria:
            u_vars[(alternative, criterion)] = pulp.LpVariable(
                f"u_{alternative}_{criterion}", lowBound=0
            )
            if verbose:
                print(
                    "Stworzono zmienną decyzyjną:",
                    u_vars[(alternative, criterion)],
                    "o dolnym ograniczeniu 0",
                )

    epsilon = pulp.LpVariable("epsilon", lowBound=-100)
    print("Stworzono zmienną decyzyjną:", epsilon, "o dolnym ograniczeniu 0")
    problem += epsilon
    print("Dodano funkcję celu:", problem.objective)

    # REFERENCE RANKING
    for a, b in preferential_info:
        problem += (
            pulp.lpSum(u_vars[(a, j)] for j in criteria)
            >= pulp.lpSum(u_vars[(b, j)] for j in criteria) + epsilon
        )

    for a, b in indiff_info:
        problem += pulp.lpSum(u_vars[(a, j)] for j in criteria) == pulp.lpSum(
            u_vars[(b, j)] for j in criteria
        )

    print("Dodano ograniczenia wynikające z rankingu referencyjnego")

    # NORMALIZATION and NON-NEGATIVITY
    breakpoints = {}
    for criterion in criteria:
        for _ in all_alternatives:
            breakpoints[criterion] = []

    for criterion in criteria:
        for alternative in all_alternatives:
            breakpoints[criterion].append((alternative, df.loc[alternative, criterion]))

    for criterion in criteria:
        breakpoints[criterion].sort(key=lambda x: x[1], reverse=True)

    u_best = [
        pulp.LpVariable(f"u_best_{criteria[i]}", lowBound=0)
        for i in range(len(criteria))
    ]
    u_worst = [
        pulp.LpVariable(f"u_worst_{criteria[i]}", lowBound=0, upBound=0)
        for i in range(len(criteria))
    ]
    problem += pulp.lpSum(u_worst) == 0
    problem += pulp.lpSum(u_best) == 1

    weights = [0.2, 0.18, 0.3, 0.32]  # TODO

    for i, criterion in enumerate(breakpoints):
        # worst
        key = (breakpoints[criterion][0][0], criterion)
        problem += u_worst[i] == 0
        problem += u_worst[i] <= u_vars[key]

        # best
        key = (breakpoints[criterion][-1][0], criterion)
        problem += u_best[i] == 1 * weights[i]
        problem += u_vars[key] <= u_best[i]

    print("Dodano ograniczenia wynikające z normalizacji i nieujemnosci")

    # MONOTONICITY
    for criterion in criteria:
        for i in range(1, len(breakpoints[criterion])):
            key1 = (breakpoints[criterion][i - 1][0], criterion)
            key2 = (breakpoints[criterion][i][0], criterion)
            # not sure about that, variables with exact same value on criterion may have different utility
            problem += u_vars[key2] >= u_vars[key1]

    print("Dodano ograniczenia wynikające z monotoniczności")
    print("Ostateczny problem do rozwiązania:")
    problem.solve()

    if verbose:
        print(problem)
        for v in problem.variables():
            print(v.name, "=", v.varValue)

    print("Status:", pulp.LpStatus[problem.status])

    return problem, u_vars, criteria, breakpoints


def plot_utility_functions(
    problem: pulp.LpProblem,
    u_vars: Dict,
    criteria: List[str],
    breakpoints: Dict[str, List[Tuple[str, float]]],
):
    if pulp.LpStatus[problem.status] == "Optimal":
        for criterion in criteria:
            sorted_alternatives = breakpoints[criterion]
            sorted_alternatives.sort(key=lambda x: x[1], reverse=False)
            x_values = sorted_alternatives
            X_axis = [value[1] for value in x_values]
            y_values = [u_vars[(value[0], criterion)].varValue for value in x_values]
            plt.figure(figsize=(15, 5))
            plt.plot(X_axis, y_values, "o-", markersize=7)
            plt.title(f"Kryterium {criterion}")

    plt.show()


def create_full_ranking_df(
    df: pd.DataFrame, problem: pulp.LpProblem, criteria: List[str]
):
    output = []
    for v in problem.variables():
        if "epsilon" not in v.name and "best" not in v.name and "worst" not in v.name:
            output.append((v.name, v.varValue))
    partial_util = [f"u{i + 1}" for i in range(len(criteria))]
    util_cols = pd.DataFrame(columns=partial_util + ["U"])
    df = pd.concat([df, util_cols], axis=1)

    criteria_util_map = {c: u for c, u in zip(criteria, partial_util)}
    for alternative, utility in output:
        _, alt, criterion = alternative.split("_")
        alt = int(alt)
        col = criteria_util_map[criterion]
        df.loc[alt, col] = utility
    df["U"] = df["u1"] + df["u2"] + df["u3"] + df["u4"]
    return df


def check_consistency(
    rank: pd.DataFrame,
    preferential_info: List[tuple],
    indiff_info: List[tuple],
    coef=1e-5,
):
    final_rank = rank.sort_values(by="U", ascending=False).index.values
    for pair in preferential_info:
        if (
            np.where(final_rank == pair[0])[0].item()
            > np.where(final_rank == pair[1])[0].item()
        ):
            print(f"Inconsistency for pair: {pair}")
            return False
    for pair in indiff_info:
        if abs(rank.loc[pair[0]].U - rank.loc[pair[1]].U) > coef:
            print(f"Inconsistency for pair: {pair}")
    return True


def obtain_relations(rank: pd.DataFrame) -> (dict, dict):
    partial_utilities = ['u'+str(i+1) for i in range(4)]
    necessarily_preferred, possibly_preffered = {}, {}

    for i, row in rank.iterrows():

        if i not in necessarily_preferred.keys():
            necessarily_preferred[i] = []
            possibly_preffered[i] = []

        for j, candidate in rank.iterrows():
            if i != j:
                if all(rank.iloc[i-1][partial_utilities] >= rank.iloc[j-1][partial_utilities]):
                    necessarily_preferred[i].append(j)
                    possibly_preffered[i].append(j)
                elif any(rank.iloc[i-1][partial_utilities] >= rank.iloc[j-1][partial_utilities]):
                    possibly_preffered[i].append(j)
                    
    return necessarily_preferred, possibly_preffered