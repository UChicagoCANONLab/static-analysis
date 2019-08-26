/// Max White

require('../../grading-scripts-s3/scratch3');
var fs = require('fs');
var arrayToCSV = require('./array-to-csv');
var Papa = require('papaparse');

module.exports = class {

    /// Initializes the grader's properties.
    init(json) {
        if (no(json)) return false;
        this.requirements = {};
        this.extensions = {};
        this.info = {
            numSprites: { val: 0, str: 'Number of sprites in project'                               },
            numScripts: { val: 0, str: 'Number of scripts in project: '                             },
            numBlocks:  { val: 0, str: 'Number of blocks in scripts: '                              },
            lDistance:  { val: 0, str: 'Number of blocks that are not present in original project'  }
        }
        return true;
    }

    /// Measures the complexity of the project JSON and compares it to the Scratch Encore original.
    grade(json, originalJson) {
        if (!this.init(json)) return;
        var project         = new Project(json,         this);
        var originalProject = new Project(originalJson, this);
        for (var sprite of project.sprites) {
            this.info.numSprites.val++;
            for (var script of sprite.scripts.filter(
                script => script.blocks[0].opcode.includes('event_when') && script.blocks.length > 1
            )) {
                this.info.numScripts.val++;
                for (var block of script.blocks) {
                    this.info.numBlocks.val++;
                }
            }
        }

        /// Calculate minimum lDistance for each script and sum them up.
        var distanceSum = 0;
        for (
            var script
            of
            project.scripts.filter(script => script.blocks[0].opcode.includes('event_when') && script.blocks.length > 1)
        ) {
            var allScripts = [];
            allScripts.push(script);
            allScripts = allScripts.concat(script.allSubscripts);
            for (var oneScript of allScripts) {
                var opcodeArray = [];
                for (var block of oneScript.blocks) {
                    opcodeArray.push(block.opcode);
                }
                /// Find the minimum distance (i.e. the best match, most probable origin, etc.).
                var minScriptDistance = 1000 * oneScript.blocks.length;
                for (var originalScript of originalProject.scripts) {
                    var originalOpcodeArray = [];
                    for (var originalBlock of originalScript.blocks) {
                        originalOpcodeArray.push(originalBlock.opcode);
                    }
                    var scriptDistance = lDistance(opcodeArray, originalOpcodeArray);
                    //console.log(scriptDistance);
                    if (minScriptDistance > scriptDistance) minScriptDistance = scriptDistance;
                }
                distanceSum += minScriptDistance;
            }
        }
        this.info.lDistance.val = distanceSum;
    }
}

/// Measures the Levenshtein distance between two Arrays.
function lDistance(arr1, arr2) {

    /// Initialize distance matrix.
    var dMatrix = [];
    for (var i = 0; i <= arr1.length; i++) {
        var column = [];
        for (var j = 0; j <= arr2.length; j++) {
            var value = 0;
            if (!i) value = j;
            if (!j) value = i;
            column.push(value);
        }
        dMatrix.push(column);
    }

    for (var j = 1; j <= arr2.length; j++) {
        for (var i = 1; i <= arr1.length; i++) {
            var swapCost = Number(arr1[i - 1] !== arr2[j - 1]);
            dMatrix[i][j] = Math.min(
                dMatrix[i - 1][j    ] + 1,
                dMatrix[i    ][j - 1] + 1,
                dMatrix[i - 1][j - 1] + swapCost
            );
        }
    }
    return dMatrix[arr1.length][arr2.length];
}

/// Creates a directory if it's not there yet and notifies the user.
function installDir(dirname) {
    if (!fs.existsSync(dirname)) {
        fs.mkdirSync(dirname);
        console.log('Created directory ' + dirname + '.');
    }
}

/// Assesses complexity of projects and compares them to their original versions.
function main() {

    /// Checks to make sure that all the necessary directories are present.
    installDir('./test-original');
    installDir('./test-classes');
    installDir('./test-results');

    /// 2D array spine. Each cell will contain a row of the table.
    var rows = [];

    /// Populates the first row of the table with headers.
    var headerRow = [
        'File', 'Studio ID', 'Teacher ID', '# Sprites', '# Scripts', '# Blocks', 'L. Distance'
    ];
    rows.push(headerRow);

    /// Gets the JSON of the original Scratch project (usually by ScratchEncore).
    var originalFilename = fs.readdirSync('./test-original')[0];
    if (originalFilename === undefined) {
        console.error('Please place the original JSON file in ./test-original.');
        return;
    }
    var originalFileJSON = JSON.parse(fs.readFileSync('./test-original/' + originalFilename, 'utf8'));

    /// Now we look into ./test-classes for folders to assess.
    var foldernames = fs.readdirSync('./test-classes');
    if (foldernames === []) {
        console.error('Please place folders containing student JSON files in ./test-classes.');
        return;
    }

    /// We also open the file that cross-references studio IDs to teacher letters.
    var classFile = fs.readFileSync('./classURLs.csv', 'utf8');
    var classTable = Papa.parse(classFile, {header: true});

    for (var foldername of foldernames) {

        /// Look up the teacher ID letter for this folder.
        var teacherID = '?';
        for (var classTableRow of classTable.data) {
            for (var x in classTableRow) {
                if (classTableRow[x].includes(foldername)) {
                    teacherID = classTableRow['Teacher ID'];
                }
            }
        }

        /// Look through all the files in the class subfolder.
        var filenames = fs.readdirSync('./test-classes/' + foldername);
        if (filenames.length) {
            for (var filename of filenames) {

                /// Get the results from the file.
                var fileJSON = JSON.parse(fs.readFileSync('./test-classes/' + foldername + '/' + filename, 'utf8'));
                var grader = new module.exports();
                grader.grade(fileJSON, originalFileJSON);

                /// Create a new row of the table.
                var currentRow = [];

                /// Fill in the row with our info.
                currentRow.push(filename);
                currentRow.push(foldername);
                currentRow.push(teacherID);
                for (var infoItem in grader.info) {
                    currentRow.push(grader.info[infoItem].val);
                }

                /// Push the row to the table.
                rows.push(currentRow);
            }
        }
    }

    /// Finally, we save the table as a .csv file.
    arrayToCSV(rows, './test-results/results.csv');
}

main();
