from ortools.sat.python import cp_model

class AIScheduler:
    def __init__(self, rules, preferences):
        self.rules = rules
        self.preferences = preferences

    def generate(self):
        model = cp_model.CpModel()
        shifts = ['A', 'B', 'C']
        num_crew = len(self.preferences)
        if num_crew == 0:
            return {"error": "No crew members available"}
        crew_vars = [[model.NewBoolVar(f'crew_{i}_shift_{s}') for s in shifts] for i in range(num_crew)]
        for i in range(num_crew):
            model.Add(sum(crew_vars[i]) == 1)
        for j in range(len(shifts)):
            model.Add(sum(crew_vars[i][j] for i in range(num_crew)) >= 1)
        preference_terms = []
        for i, pref in enumerate(self.preferences):
            preferred = pref.get('preferred_shifts', [])
            for j, shift in enumerate(shifts):
                if shift in preferred:
                    preference_terms.append(crew_vars[i][j])
        model.Maximize(sum(preference_terms))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            assignments = {}
            for i in range(num_crew):
                for j, shift in enumerate(shifts):
                    if solver.Value(crew_vars[i][j]):
                        assignments[str(self.preferences[i].get("id", i))] = {
                            "name": self.preferences[i].get("name", f"Crew {i}"),
                            "shift": shift
                        }
            return assignments
        return {"error": "No feasible schedule found"}