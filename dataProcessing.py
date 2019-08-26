# By Marco Anaya


# python3 processData.py (path)

import sys
import os

import pandas as pd


def aggregate(project, module):
    data = {
        'student_performance': [],
        'class_distributions': [],
        'class_performance_per_req': []
    }

    path = "./" + project + "/" + module + "/"

    decimal_place = 2

    for grade in os.listdir(path + 'csv/'):
        if not os.path.isdir(path + 'csv/' + grade) or 'aggregated' in grade:
            continue

        grade_dir = path + 'csv/' + grade + '/'
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
    print("Creating data files for " + module + ":")
    for name, d in data.items():
        file_path = path + 'csv/' + module + '_' + name + '.csv'
        
        data[name] = pd.DataFrame(d, columns=d[0].keys())
        data[name].to_csv(file_path, index=False)
        print(" ", file_path)
    
    return data


if __name__ == '__main__':
    aggregate(sys.argv[1], sys.argv[2])
