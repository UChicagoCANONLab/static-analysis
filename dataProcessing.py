# By Marco Anaya


# python3 processData.py (module)

import sys
import os

import pandas as pd


data = {
    'student_performance': [],
    'class_distributions': [],
    'class_performance_per_req': []
}


def main():
    module = sys.argv[1]
    module += '' if module[-1] == '/' else '/'
    modname = module.strip('/')

    decimal_place = 2

    for grade in os.listdir(module + 'csv/'):
        if not os.path.isdir(module + 'csv/' + grade) or 'aggregated' in grade:
            continue

        grade_dir = module + 'csv/' + grade + '/'
        # for each classroom of data, appending a row/rows to each data array
        for filename in os.listdir(grade_dir):
            if not filename.endswith(".csv"):
                continue

            class_data = pd.read_csv(grade_dir + filename) \
                           .drop(['Error grading project'], axis=1)

            student_count = len(class_data.index)
            req_count = len(class_data.columns) - 1

            # splitting filename into teacher and studio IDs
            tID, cID = filename.split('.')[0].split('-')

            # general information that will be the first few rows of each csv
            class_info = {
                "Grade": grade,
                "Teacher ID": tID,
                "Studio ID": cID,
                "Class Size": student_count
            }

            # aggregating row of percentage of completion by class by requirement with totals on last column
            possible_score = student_count * req_count
            score_totals = class_data.drop('ID', axis=1).sum(axis=0)
            by_reqs_row = {
                **class_info,
                **(100 * score_totals / student_count).round(decimal_place).to_dict(),
                **{'Total': (score_totals.sum() * 100 / possible_score).round(decimal_place)}
            }
            data['class_performance_per_req'].append(by_reqs_row)

            # aggregating row of class_distributions by class
            distr_row = pd.concat([class_data, pd.DataFrame(class_data.sum(axis=1), columns=['Sum'])], axis=1) \
                .groupby('Sum').Sum.count() \
                .reindex(range(req_count + 1), fill_value=0).to_dict()
            data['class_distributions'].append({**class_info, **distr_row})

            # aggregating rows of performance by student
            for (i, val) in class_data.sum(axis=1, numeric_only=True).iteritems():
                data['student_performance'].append({**class_info, **{
                    "Student ID": class_data.at[i, 'ID'],
                    "Score": val,
                    "Out of": req_count,
                    "Percentage": round((val / req_count), decimal_place)
                }})
    print("Creating data files for " + modname + ":")
    for name, d in data.items():
        path = module + 'csv/' + modname + '_' + name + '.csv'
        print(" ", path)
        pd.DataFrame(d, columns=d[0].keys()) \
            .to_csv(path, index=False)
    sys.exit()


if __name__ == '__main__':
    main()
