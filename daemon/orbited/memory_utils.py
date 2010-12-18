import objgraph

def instance_counts(instances):
    totals = {}
    for instance in instances:
        klassname = instance.__class__.__name__
        if klassname not in totals:
            totals[klassname] = 0
        totals[klassname] += 1
    return sorted(totals.items(), key=lambda (klassname, count): -count)

