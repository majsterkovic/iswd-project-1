import pandas as pd
import pulp
import matplotlib.pyplot as plt
import numpy as np
import pprint as pp
# from networkx import graphvis_
from typing import List, Tuple, Dict

plt.style.use("ggplot")
pulp.LpSolverDefault.msg = 0

def solve_lp_problem(
    df: pd.DataFrame,
    preferential_info: List[tuple],
    indifference_info: List[tuple],
):
    criteria = df.columns.tolist()
    alternatives = {x for t in (preferential_info + indifference_info) for x in t}

    problem = pulp.LpProblem("UTA", pulp.LpMaximize)

    u_vars = {}
    for alternative in alternatives:
        for criterion in criteria:
            value = df.loc[alternative, criterion]
            criterion_no = criteria.index(criterion) + 1
        
            u_vars[(criterion, value)] = pulp.LpVariable(
                f"u{criterion_no}({value})", lowBound=0, upBound=1
            )

    epsilon = pulp.LpVariable("epsilon", lowBound=0)
    problem += epsilon

    for a, b in preferential_info:
        problem += (
            pulp.lpSum(u_vars[(c, df.loc[a, c])] for c in criteria)
            >= pulp.lpSum(u_vars[(c, df.loc[b, c])] for c in criteria) + epsilon
        )

    for a, b in indifference_info:
        problem += pulp.lpSum(u_vars[(c, df.loc[a, c])] for c in criteria) == pulp.lpSum(
            u_vars[(c, df.loc[b, c])] for c in criteria
        )

    worst_values = {criterion: df[criterion].max() for criterion in criteria}
    best_values = {criterion: df[criterion].min() for criterion in criteria}
    breakpoints = {criterion: sorted(df[criterion].unique()) for criterion in criteria}

    u_best = []
    u_worst = []

    for criterion, value in worst_values.items():
        if (criterion, value) not in u_vars:
            criterion_no = criteria.index(criterion) + 1
            u_vars[(criterion, value)] = pulp.LpVariable(f"u{criterion_no}({value})", lowBound=0, upBound=1)
        u_worst.append(u_vars[(criterion, value)])

    for criterion, value in best_values.items():
        if (criterion, value) not in u_vars:
            criterion_no = criteria.index(criterion) + 1
            u_vars[(criterion, value)] = pulp.LpVariable(f"u{criterion_no}({value})", lowBound=0, upBound=1)
        u_best.append(u_vars[(criterion, value)])


    for criterion in breakpoints.keys():
        for value in breakpoints[criterion]:
            if (criterion, value) not in u_vars:
                criterion_no = criteria.index(criterion) + 1
                u_vars[(criterion, value)] = pulp.LpVariable(f"u{criterion_no}({value})", lowBound=0, upBound=1)

    problem += pulp.lpSum(u_worst) == 0
    problem += pulp.lpSum(u_best) == 1

    weights_vars = [pulp.LpVariable(f"w{i}", lowBound=0, upBound=1) for i in range(len(criteria))]
    for weight in weights_vars:
        problem += weight >= 0 + 0.0001
        problem += weight <= 0.5

    for criterion in criteria:
        problem += u_vars[(criterion, best_values[criterion])] == 1 * weights_vars[criteria.index(criterion)]

        for i, value in enumerate(breakpoints[criterion]):

            if value == best_values[criterion]:
                continue

            key1 = (criterion, breakpoints[criterion][i])
            key2 = (criterion, breakpoints[criterion][i - 1])

            problem += u_vars[key1] <= u_vars[key2]

    problem.solve()
    print("Status:", pulp.LpStatus[problem.status])
    for v in problem.variables():
        print(v.name, "=", v.varValue)

    return problem, u_vars, criteria, breakpoints


def solve_lp_problem_gms(
    df: pd.DataFrame,
    preferential_info: List[tuple],
    indiff_info: List[tuple],
    verbose=True
):
    criteria = df.columns.tolist()
    all_alternatives = df.index.tolist()
    info = preferential_info + indiff_info
    reference_alternatives = list(set([x for pair in info for x in pair]))


    print("Wszystkie alternatywy:", all_alternatives)
    print("Alternatywy referencyjne:", reference_alternatives)

    pulp.LpSolverDefault.msg = 0
    problem = pulp.LpProblem("UTA", pulp.LpMaximize)
    print("Kryteria:", criteria)

    # VARIABLES
    u_vars = {}
    for alternative in all_alternatives:
        for criterion in criteria:
            value = df.loc[alternative, criterion]
            criterion_no = criteria.index(criterion) + 1

            u_vars[(criterion, value)] = pulp.LpVariable(
                f"u{criterion_no}({value})", lowBound=0
            )
            if verbose:
                print(
                    "Stworzono zmienną decyzyjną:",
                    u_vars[(criterion, value)],
                    "o dolnym ograniczeniu 0",
                )

    epsilon = pulp.LpVariable("epsilon", lowBound=-100)
    print("Stworzono zmienną decyzyjną:", epsilon, "o dolnym ograniczeniu 0")
    problem += epsilon
    print("Dodano funkcję celu:", problem.objective)

    # REFERENCE RANKING
    for a, b in preferential_info:
        problem += (
            pulp.lpSum(u_vars[(c, df.loc[a, c])] for c in criteria)
            >= pulp.lpSum(u_vars[(c, df.loc[b, c])] for c in criteria) + epsilon
        )

    for a, b in indiff_info:
        problem += pulp.lpSum(u_vars[(c, df.loc[a, c])] for c in criteria) == pulp.lpSum(
            u_vars[(c, df.loc[b, c])] for c in criteria
        )

    print("Dodano ograniczenia wynikające z rankingu referencyjnego")

    # NORMALIZATION and NON-NEGATIVITY

    worst_values = {criterion: df[criterion].max() for criterion in criteria}
    best_values = {criterion: df[criterion].min() for criterion in criteria}
    u_best = []
    u_worst = []

    for criterion, value in worst_values.items():
        u_worst.append(u_vars[(criterion, value)])

    for criterion, value in best_values.items():
        u_best.append(u_vars[(criterion, value)])

    # globally worst and best
    problem += pulp.lpSum(u_worst) == 0
    problem += pulp.lpSum(u_best) == 1

    weights = [0.2, 0.18, 0.3, 0.32]  # TODO

    breakpoints = {}
    for criterion in criteria:
        for _ in all_alternatives:
            breakpoints[criterion] = []
    for criterion in criteria:
        for alternative in all_alternatives:
            breakpoints[criterion].append((alternative, df.loc[alternative, criterion]))

    for criterion in criteria:
        breakpoints[criterion].sort(key=lambda x: x[1], reverse=True)

    for i, criterion in enumerate(breakpoints):
        # worst from reference
        value = df.loc[breakpoints[criterion][0][0], criterion]
        key = (criterion, value)
        problem += u_worst[i] == 0
        problem += u_worst[i] <= u_vars[key]

        # best from reference
        value = df.loc[breakpoints[criterion][-1][0], criterion]
        key = (criterion, value)
        problem += u_best[i] == 1 * weights[i]
        problem += u_vars[key] <= u_best[i]

    print("Dodano ograniczenia wynikające z normalizacji i nieujemnosci")

    # MONOTONICITY
    for criterion in criteria:
        for i in range(1, len(breakpoints[criterion])):

            couple = (breakpoints[criterion][i - 1][0], breakpoints[criterion][i][0])
            couple_reversed = (breakpoints[criterion][i][0], breakpoints[criterion][i - 1][0])

            if couple in indiff_info or couple_reversed in indiff_info:
                continue

            value1 = df.loc[breakpoints[criterion][i - 1][0], criterion]
            value2 = df.loc[breakpoints[criterion][i][0], criterion]

            key1 = (criterion, value1)
            key2 = (criterion, value2)
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

def most_representative_function(
        u_vars: Dict,
        df: pd.DataFrame,
        criteria: List[str],
        problem: pulp.LpProblem,
        necessary_preferred: Dict,
        possibly_preferred: Dict,
):
    
    delta = pulp.LpVariable("delta", lowBound=0)
    
    epsilon = pulp.LpVariable("epsilon", lowBound=0)

    for a_variant in necessary_preferred.keys():
        for b_variant in necessary_preferred[a_variant]:
           #if a is necessarily preferred to b
           # but b is not necessarily preferred to a
            # add constraint to problem U(a) > U(b) + epsilon
            if a_variant not in necessary_preferred[b_variant]:
                problem += pulp.lpSum(u_vars[(c, df.loc[a_variant, c])] for c in criteria) >= pulp.lpSum(u_vars[(c, df.loc[b_variant, c])] for c in criteria) + epsilon

    for c_variant in possibly_preferred.keys():
            #if c is not necessarily preferred to d
            # and d is not necessarily preferred to c
            # add constraint to problem U(c)-U(d) <= delta and U(d)-U(c) <= delta
            for d_variant in possibly_preferred[c_variant]:
                if c_variant not in possibly_preferred[d_variant]:
                    problem += pulp.lpSum(u_vars[(c, df.loc[c_variant, c])] for c in criteria) - pulp.lpSum(u_vars[(c, df.loc[d_variant, c])] for c in criteria) <= delta
                    problem += pulp.lpSum(u_vars[(c, df.loc[d_variant, c])] for c in criteria) - pulp.lpSum(u_vars[(c, df.loc[c_variant, c])] for c in criteria) <= delta

    # change objective function to minimize epsilon to maximize M*epsilon - delta
    # create M variable

    problem += 1000000 * epsilon - delta
    print("Ostateczny problem do rozwiązania:")
    print(problem)
    problem.solve()
    print("Status:", pulp.LpStatus[problem.status])
    for v in problem.variables():
        print(v.name, "=", v.varValue)


f = {}

def plot_utility_functions(
    problem: pulp.LpProblem,
    u_vars: Dict,
    criteria: List[str],
    breakpoints: Dict[str, List[Tuple[str, float]]],
):
    if pulp.LpStatus[problem.status] == "Optimal":
        for criterion in criteria:
            f[criterion] = {}
            series = []
            for key in u_vars.keys():
                if key[0] == criterion:
                    x, y = key[1], u_vars[key].varValue
                    if y is not None:
                        series.append((x, y))
                        f[criterion][x] = y
            series.sort(key=lambda x: x[0])
            plt.figure(figsize=(15, 5))
            plt.plot([x[0] for x in series], [x[1] for x in series], "o-", markersize=7)
            plt.title(f"Kryterium {criterion}")
    pp.pprint(f)
    plt.show()


def create_full_ranking_df(
    df: pd.DataFrame, problem: pulp.LpProblem, criteria: List[str]
):
    partial_util = [f"u{i + 1}" for i in range(len(criteria))]
    util_cols = pd.DataFrame(columns=partial_util + ["U"])
    df = pd.concat([df, util_cols], axis=1)

    for i, row in df.iterrows():
        for j, criterion in enumerate(criteria):
            value = row[criterion]
            if value not in f[criterion]:
                interpolate(value, criterion)
            df.loc[i, f"u{j+1}"] = f[criterion][value]

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


def interpolate(value: float, criterion: str):
    min_diff_plus=1.0
    min_diff_minus=1.0
    cur_xi = -1
    cur_xj = -1
    xi = -1
    xj = -1
    
    for candidate in f[criterion].keys():
        if candidate > value:
            diff_plus = candidate - value
            if diff_plus < min_diff_plus:
                min_diff_plus = diff_plus
                xj = candidate
        else:
            diff_minus = value - candidate
            if diff_minus < min_diff_minus:
                min_diff_minus = diff_minus
                xi = candidate
                
    u_xi = f[criterion][xi]
    u_xj = f[criterion][xj]
    f[criterion][value] = u_xi + ((u_xi - u_xj) / (xi - xj)) * (value - xi)
    