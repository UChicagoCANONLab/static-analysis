/// Local tester for grading scripts
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Reformatted to make use of object to csv library
// Adapted from code by Zack Crenshaw
// Adapted from code by Max White

const fs  = require('fs');
const ObjectsToCsv = require('objects-to-csv');

const projectGradersDir = {
    ['encore']: 'grading-scripts-s3', 
    ['act-one']: 'act1-grading-scripts'
}

const is = it => (it !== undefined && it !== null && it != {});


function main([project, mod, tID, grade, studioID, studioPath, verbose=null]) {

    let GraderClass = require(`../${projectGradersDir[project]}/${mod}.js`);

    let reqs = {path: `./${project}/${mod}/csv/${grade}/${tID}-${studioID}.csv`, data: []};
    let deepDive = {path: `./${project}/${mod}/csv/${mod}-deep-dive.csv`, data: []};


    let fileNames = fs.readdirSync(studioPath);
    let isDeepDive = true;

    for (let name of fileNames.filter(name => /_*\.json/g.test(name) )) {
        
        let json = require(`${studioPath}/${name}`);
        let grader = new GraderClass();

        let studentID = name.replace(".json","");
        let reqsRow = {ID: studentID, ['Error grading project']: 0};
        let deepDiveRow = {['Teacher ID']: tID, ['Classroom ID']: studioID, ['Student ID']: studentID}

        if (verbose) console.log(studentID);

        //Run grade and output results
        try {
            grader.grade(json, '');
            if (is(grader.requirements)) 
                for (let item of Object.values(grader.requirements)) 
                    reqsRow[item.str] = ((item.bool) ? (1) : (0));
            /* if (is(grader.extensions)) {
                for (var item of Object.values(grader.extensions)) {
                    row[item.str] = ((item.bool) ? (1) : (0));
                }
            } */
            if (isDeepDive && is(grader.info)) {
                deepDiveRow = {...deepDiveRow, ...grader.info};
                deepDiveRow.blockTypes = [... deepDiveRow.blockTypes].reduce((acc, b) => acc + b + '|', '');
            } else {
                isDeepDive = false;
            }
        }
        //If there was an error, report it
        catch(err) {
            reqsRow['Error grading project'] = 1;
            deepDiveRow['Error grading project'] = 1;
            console.log('Error grading project:', studentID)
            console.log(err);
        }

        reqs.data.push(reqsRow);
        if (isDeepDive) deepDive.data.push(deepDiveRow)
    }

    // converting json to csv file, moving the row with the most columns to the top
    // so that the conversion module functions properly
    var largestRowIndex = reqs.data.map(row => Object.keys(row).length)
        .reduce((a, b, i) => a[0] < b? [b, i] : a, [Number.MIN_VALUE, -1])[1];
    var tmp = reqs.data[0];
    reqs.data[0] = reqs.data[largestRowIndex];
    reqs.data[largestRowIndex] = tmp;

    try {new ObjectsToCsv(reqs.data).toDisk(reqs.path); } 
    catch(err) {console.log(reqs.data); }
    if (isDeepDive) {
        try { new ObjectsToCsv(deepDive.data).toDisk(deepDive.path, { append: true }); } 
        catch(err) {console.log(deepDive.data); }
    }
}

main(process.argv.slice(2));



  
  