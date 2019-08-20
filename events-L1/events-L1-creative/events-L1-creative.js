/// GRADER //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

require('../../../grading-scripts-s3/scratch3');
var EventsL1 = require('../../../grading-scripts-s3/events-L1');

module.exports = class EventsL1Creative extends EventsL1 {

    init() {
        super.init();
        this.creative = {

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
        var defaultProject = new Project(require('../test-projects/SE-events-L1.json'), this);
        var defaultCostumeIDs = [];
        var defaultSoundIDs   = [];
        var defaultMessages   = [];
        for (var target of defaultProject.targets) {
            if (target.costumes !== undefined && target.costumes.length) {
                for (var costume of target.costumes) {
                    defaultCostumeIDs.push(costume.assetId);
                }
            }
            if (target.sounds !== undefined && target.sounds.length) {
                for (var sound of target.sounds) {
                    defaultSoundIDs.push(sound.assetId);
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
                if (!defaultCostumeIDs.includes(costume.assetID)) {
                    this.creative.newBackdrops.val++;
                }
            }
        }

        /// Find new costumes in sprites
        for (var sprite of project.sprites) {
            for (var costume of sprite.costumes) {
                if (!defaultCostumeIDs.includes(costume.assetID)) {
                    this.creative.newCostumes.val++;
                }
            }
        }

        /// Find new sounds in all targets
        for (var target of project.targets) {
            for (var sound of target.sounds) {
                if (!defaultSoundIDs.includes(sound.assetID)) {
                    this.creative.newSounds.val++;
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
            for (var script of target.scripts.filter(script => script.blocks[0].opcode.includes('event_'))) {
                for (var block of script.blocks) {
                    if (oldBlocksList.includes(block.opcode)) {
                        this.creative.oldBlocks.val.push(block.opcode);
                    }
                    else if (newBlocksList.includes(block.opcode)) {
                        this.creative.newBlocks.val.push(block.opcode);
                    }
                    else {
                        this.creative.otherBlocks.val.push(block.opcode);
                    }
                }
            }
        }

        /// Remove duplicates
        for (var val of [this.creative.oldBlocks.val, this.creative.newBlocks.val, this.creative.otherBlocks.val]) {
            val = Array.from(new Set(val));
        }

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
            'family'
        ];
        for (var target of project.targets) {
            for (var script of target.scripts.filter(script => script.block[0].opcode.includes('event_'))) {
                for (var block of script.blocks) {
                    if (block.opcode === 'looks_sayforsecs' || block.opcode === 'looks_say') {
                        var message = block.inputs.MESSAGE[1][1];
                        if (!defaultMessages.includes(message)) {
                            for (var word of familyWords) {
                                var regexp = new RegExp(word, 'g');
                                this.creative.familyCount.val += (message.match(regexp) || []).length;
                                console.log(this.creative.familyCount.val);
                            }
                        }
                    }
                }
            }
        }
    }
}

/// CRAWLER /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var project_count = 0;
var gradeObj = new EventsL1Creative();
var XMLHttpRequest = require('xhr2');
var arrayToCSV = require('./arrayToCSV');
var results = [];
var rows = [];
var firstRow = [
    'Studio ID',
    'Project ID',
    'New backrops',
    'New costumes',
    'New sounds',
    'M01 blocks',
    'M02 blocks',
    'Other blocks',
    'Family refs'
];
rows.push(firstRow);

class ProjectIdentifier {
    constructor(projectOverview, studioID) {
        this.id = projectOverview.id;
        this.author = projectOverview.author.id;
        this.studioID = studioID;
    }
}

function get(url) {
    return new Promise(function (resolve, reject) {
        var request = new XMLHttpRequest();
        request.open('GET', url);
        request.onload = resolve;
        request.onerror = reject;
        request.send();
    });
}

async function crawl(studioID, offset, projectIdentifiers) {
    if (!offset) console.log('Grading studio ' + studioID);
    get('https://chord.cs.uchicago.edu/scratch/studio/' + studioID + '/offset/' + offset)
        .then(function (result) {
            var studioResponse = JSON.parse(result.target.response);
            /// Keep crawling or return?
            if (studioResponse.length === 0) {
                keepGoing = false;
                for (var projectIdentifier of projectIdentifiers) {
                    gradeProject(projectIdentifier);
                }
                return;
            }
            else {
                for (var projectOverview of studioResponse) {
                    projectIdentifiers.push(new ProjectIdentifier(projectOverview, studioID));
                }
                crawl(studioID, offset + 20, projectIdentifiers);
            }
        });
}

function gradeProject(projectIdentifier) {
    var projectID = projectIdentifier.id;
    var projectAuthor = projectIdentifier.author;
    console.log('Grading project ' + projectID);
    get('https://chord.cs.uchicago.edu/scratch/project/' + projectID)
        .then(function (result) {
            var project = JSON.parse(result.target.response);
            if (project.targets === undefined) {
                console.log('Project ' + projectID + ' could not be found');
                return;
            }
            try {
                analyze(project, projectAuthor, projectID, projectIdentifier.studioID);
            }
            catch (err) {
                console.log('Error grading project ' + projectID);
            }
        });
}

function analyze(fileObj, user, id, studioID) {
    try {
        gradeObj.grade(fileObj, id);
        var copy = {};
        Object.assign(copy, gradeObj);
        results.push()
    }
    catch (err) {
        console.log('Error grading project ' + id);
    }
    var row = [];
    row.push(studioID);
    row.push(id);
    for (var item in gradeObj.creative) {
        var val = gradeObj.creative[item].val.toString();
        row.push(val);
    }
    rows.push(row);
    arrayToCSV(rows, './results.csv');
    project_count++;
    console.log(project_count);
}

/// MAIN ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var studioIDs = [];
for (var studioID of studioIDs) {
    crawl(studioID, 0, []);
}
