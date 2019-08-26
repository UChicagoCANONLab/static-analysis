/// Max White

require('../../grading-scripts-s3/scratch3');
var fs = require('fs');
var arrayToCSV = require('./array-to-csv');
var Papa = require('papaparse');
var EventsL1 = require('../../grading-scripts-s3/events-L1');

module.exports = class EventsL1Creative extends EventsL1 {

    init() {
        super.init();
        this.info = {

            /// Assets
            newBackdrops:     { val: 0,  str: 'Number of new backdrops (present in project, but not present in Scratch Encore original).' },
            newCostumes:      { val: 0,  str: 'Number of new costumes in project.'                                                        },
            newSounds:        { val: 0,  str: 'Number of new sounds in project.'                                                          },

            /// Blocks
            oldBlocks:        { val: [], str: 'Opcodes of blocks used in project that were introduced before this lesson.'                },
            newBlocks:        { val: [], str: 'Opcodes of blocks that were introduced in this lesson.'                                    },
            otherBlocks:      { val: [], str: 'Opcodes of blocks that students have not yet been taught.'                                 },

            /// Self-involvement
            familyCount:      { val: 0,  str: 'Number of times student references their family in the project.'                           }
        }
    }

    grade(json, user) {
        this.init();
        super.grade(json, user);

        /// Identify default asset IDs and messages provided by starter project
        var defaultProject = new Project(require('./test-original/project.json'), this);
        var defaultCostumeIds = [];
        var defaultSoundIds   = [];
        var defaultMessages   = [];
        for (var target of defaultProject.targets) {
            if (target.costumes !== undefined && target.costumes.length) {
                for (var costume of target.costumes) {
                    defaultCostumeIds.push(costume.assetId);
                }
            }
            if (target.sounds !== undefined && target.sounds.length) {
                for (var sound of target.sounds) {
                    defaultSoundIds.push(sound.assetId);
                }
            }
            for (var script of target.scripts) {
                for (var block of script.blocks) {
                    if (block.opcode === 'looks_sayforsecs' || block.opcode === 'looks_say') {
                        defaultMessages.push(block.inputs.MESSAGE[1][1]);
                    }
                }
            }
        }
        var project = new Project(json, this);

        /// Find new backdrops in stage
        for (var stage of project.targets.filter(target => target.isStage)) {
            for (var costume of stage.costumes) {
                if (!defaultCostumeIds.includes(costume.assetId)) {
                    this.info.newBackdrops.val++;
                }
            }
        }

        /// Find new costumes in sprites
        for (var sprite of project.sprites) {
            for (var costume of sprite.costumes) {
                if (!defaultCostumeIds.includes(costume.assetId)) {
                    this.info.newCostumes.val++;
                }
            }
        }

        /// Find new sounds in all targets
        for (var target of project.targets) {
            for (var sound of target.sounds) {
                if (!defaultSoundIds.includes(sound.assetId)) {
                    this.info.newSounds.val++;
                }
            }
        }

        /// Find old, new, and other blocks in targets
        var oldBlocksList = [
            'event_whenflagclicked',
            'looks_sayforsecs',
            'motion_movesteps',
            'motion_gotoxy'
        ];
        var newBlocksList = [
            'looks_changesizeby',
            'looks_setsizeto',
            'looks_gotofrontback',
            'event_whenthisspriteclicked',
            'event_whenkeypressed'
        ];
        for (var target of project.targets) {
            for (var script of target.scripts.filter(script => script.blocks.length > 1 && script.blocks[0].opcode.includes('event_'))) {
                for (var block of script.blocks) {
                    if (oldBlocksList.includes(block.opcode)) {
                        this.info.oldBlocks.val.push(block.opcode);
                    }
                    else if (newBlocksList.includes(block.opcode)) {
                        this.info.newBlocks.val.push(block.opcode);
                    }
                    else {
                        this.info.otherBlocks.val.push(block.opcode);
                    }
                }
            }
        }

        /// Remove duplicates
        this.info.oldBlocks.val = this.info.oldBlocks.val.length;
        this.info.newBlocks.val = this.info.newBlocks.val.length;
        this.info.otherBlocks.val = this.info.otherBlocks.val.length;

        /// Find personal involvement in sprites' scripts
        var familyWords = [
            'mother',
            'father',
            'brother',
            'sister',
            'sibling',
            'mom',
            'dad',
            'grandma',
            'grandpa',
            'child',
            'cousin',
            'aunt',
            'uncle',
            'family',
            'families'
        ];
        for (var target of project.targets) {
            for (var script of target.scripts.filter(script => script.blocks.length > 1 && script.blocks[0].opcode.includes('event_'))) {
                for (var block of script.blocks) {
                    if (block.opcode === 'looks_sayforsecs' || block.opcode === 'looks_say') {
                        var message = block.inputs.MESSAGE[1][1];
                        if (!defaultMessages.includes(message)) {
                            for (var word of familyWords) {
                                var regexp = new RegExp(word, 'g');
                                this.info.familyCount.val += (message.match(regexp) || []).length;
                            }
                        }
                    }
                }
            }
        }
    }
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
        'File',
        'Studio ID',
        'Teacher ID',
        'New Backdrops',
        'New Costumes',
        'New Sounds',
        'M1 Blocks',
        'M2 Blocks',
        'Unseen Blocks',
        'Family References',
        'Rq1', 'Rq2', 'Rq3', 'Rq4',
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
                for (var requirement in grader.requirements) {
                    currentRow.push(Number(grader.requirements[requirement].bool));
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
