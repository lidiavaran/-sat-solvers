from itertools import product
import time
import random

# -----------------------------
# Rezoluție (Resolution Method)
# -----------------------------

def is_tautology(clause):
    return any(-lit in clause for lit in clause)

def resolve(ci, cj):
    resolvents = []
    for li in ci:
        if -li in cj:
            new_clause = list(set(ci + cj) - {li, -li})
            if not is_tautology(new_clause):
                resolvents.append(new_clause)
    return resolvents

def resolution(clauses):
    new = set()
    clauses = [frozenset(c) for c in clauses]
    while True:
        pairs = [(ci, cj) for i, ci in enumerate(clauses)
                          for cj in clauses[i+1:]]
        for (ci, cj) in pairs:
            resolvents = resolve(list(ci), list(cj))
            for res in resolvents:
                f_res = frozenset(res)
                if not res:
                    return False  # empty clause => unsatisfiable
                if f_res not in clauses:
                    new.add(f_res)
        if new.issubset(clauses):
            return True  # no new info => satisfiable
        clauses.extend(new)

# --------------------------------
# Davis–Putnam Algorithm (DP)
# --------------------------------

def dp(clauses):
    if not clauses:
        return True
    if [] in clauses:
        return False
    vars_ = set(abs(lit) for clause in clauses for lit in clause)
    var = next(iter(vars_))
    pos = [c for c in clauses if var in c]
    neg = [c for c in clauses if -var in c]
    rest = [c for c in clauses if var not in c and -var not in c]
    new_clauses = []
    for ci in pos:
        for cj in neg:
            resolvent = list(set(ci + cj) - {var, -var})
            if resolvent not in new_clauses:
                new_clauses.append(resolvent)
    return dp(rest + new_clauses)

# --------------------------------------
# DPLL Algorithm with Heuristics
# --------------------------------------

def simplify(clauses, lit):
    return [[x for x in c if x != -lit] for c in clauses if lit not in c]

def dpll(clauses):
    if not clauses:
        return True
    if [] in clauses:
        return False
    # Unit propagation
    units = [c[0] for c in clauses if len(c) == 1]
    for u in units:
        clauses = simplify(clauses, u)
    # Pure literal elimination
    literals = {lit for c in clauses for lit in c}
    for lit in literals.copy():
        if -lit not in literals:
            clauses = [c for c in clauses if lit not in c]
    # Jeroslow-Wang heuristic
    scores = {lit: sum(2 ** (-len(c)) for c in clauses if lit in c) for lit in literals}
    if not scores:
        return True
    l = max(scores, key=scores.get)
    return dpll(simplify(clauses, l)) or dpll(simplify(clauses, -l))

# -----------------------------
# Helper: generate random 3-SAT
# -----------------------------

def generate_3sat_instance(n_vars, n_clauses):
    clauses = []
    for _ in range(n_clauses):
        clause = set()
        while len(clause) < 3:
            var = random.randint(1, n_vars)
            sign = random.choice([-1, 1])
            clause.add(sign * var)
        clauses.append(list(clause))
    return clauses

# -----------------------------
# Benchmark test (timing)
# -----------------------------

def test_algorithms(n_vars):
    m = 2 * n_vars
    clauses = generate_3sat_instance(n_vars, m)

    start = time.time()
    result_res = resolution([list(c) for c in clauses])
    t_res = time.time() - start

    start = time.time()
    result_dp = dp([list(c) for c in clauses])
    t_dp = time.time() - start

    start = time.time()
    result_dpll = dpll([list(c) for c in clauses])
    t_dpll = time.time() - start

    print(f'n = {n_vars} | Res: {t_res:.4f}s | DP: {t_dp:.4f}s | DPLL: {t_dpll:.4f}s')
    return t_res, t_dp, t_dpll

# -----------------------------
# Run for specific n
# -----------------------------

if __name__ == '__main__':
    for n in [3, 4, 5, 6]:
        test_algorithms(n)
