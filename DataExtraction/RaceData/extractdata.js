// this code was run with Node js to extract the data from TFeed. it extracts
// .js and .zip files from the platform and runs the scripts in those files to
// extract timetables representing the race data and converts it into a
// structured format.

var ntDriversTable = [];

var races = {};
var timetable = {};

var fs = require('fs');
var http = require('https');
var JSZip = require('jszip');


function isFunction(a) {
    return typeof a == 'function';
}

function isArray(a) {
    return isObject(a) && a.constructor == Array;
}

function isObject(a) {
    return (a && typeof a == 'object') || isFunction(a);
}

function isDivisible(number, n) {
    if (number % n == 0) { return true; }
    else { return false; }
}

function ndd_f(d_info) {
    ntDriversTable = [];
    for (var i = 0; i < d_info.length; i++) {
        ntDriversTable[i] = [];
        ntDriversTable[i][0] = d_info[i][0];
        ntDriversTable[i][1] = d_info[i][1];
        ntDriversTable[i][2] = d_info[i][2];
        ntDriversTable[i][3] = d_info[i][3];
    }
    return ntDriversTable;
}

function ntt_f(version, timestamp, s_info, w_info, t_info) {
    sessioninfo = [];
    sessioninfo['timestamp'] = timestamp;
    sessioninfo['flag'] = s_info[0];
    sessioninfo['type'] = s_info[1];
    sessioninfo['remaining'] = s_info[2];
    sessioninfo['weather'] = w_info;

    timetable = {};
    timetable['version'] = version;

    for (var i = 0; i < ntDriversTable.length; i++) {
        var d_name = ntDriversTable[i][0];
        var d_number = ntDriversTable[i][1];
        var d_startpos = ntDriversTable[i][2];
        var d_points = ntDriversTable[i][3];

        try {
            timetable[d_name] = {};
            timetable[d_name]['updated'] = 0
            timetable[d_name]['state'] = t_info[i][0];
            timetable[d_name]['lap'] = t_info[i][1];
            timetable[d_name]['lap_time'] = t_info[i][2];
            timetable[d_name]['position'] = t_info[i][3];
            timetable[d_name]['gap'] = t_info[i][4];
            timetable[d_name]['interval'] = t_info[i][5];
            timetable[d_name]['pits'] = t_info[i][6];
            timetable[d_name]['best_time'] = t_info[i][7];
            timetable[d_name]['driver_number'] = d_number;
            timetable[d_name]['speed'] = t_info[i][8];
            timetable[d_name]['gear'] = t_info[i][9];
            timetable[d_name]['gear_switches'] = t_info[i][10];
            timetable[d_name]['drs'] = t_info[i][11];
            timetable[d_name]['lap_pos'] = t_info[i][12];
            timetable[d_name]['engine_rpm'] = t_info[i][13];
            timetable[d_name]['tyre_compound'] = t_info[i][14];
            timetable[d_name]['start_pos'] = d_startpos;
            timetable[d_name]['points'] = d_points;
            timetable[d_name]['speed_traps'] = t_info[i][15];
            timetable[d_name]['max_speed_traps'] = t_info[i][16];
            timetable[d_name]['s1'] = t_info[i][17];
            timetable[d_name]['s2'] = t_info[i][18];
            timetable[d_name]['s3'] = t_info[i][19];

            if (isArray(t_info[i][20])) {
                timetable[d_name]['best_times'] = t_info[i][20];
            }
            if (isArray(t_info[i][21])) {
                timetable[d_name]['sector_segments'] = t_info[i][21];
            }

            timetable[d_name]['throttle'] = t_info[i][22];
            timetable[d_name]['break'] = t_info[i][23];
        } catch {
            continue;
        }
    }
    return timetable;
}

function fetchNddScript(url) {
    const promise = fetch(url)
        .then(response => { return response.text(); });
    return promise;
}

function fetchDrivers(year, version) {
    var vs = version.toString();
    var url = "https://f1.tfeed.net/drivers/eng_"
        + year + "_" + vs + ".js";
    try {
        const promise = fetch(url)
            .then(response => { return response.text(); });
        return promise;
    } catch { SyntaxError } { return; }
}

function fetchTeams(year) {
    const url = "https://f1.tfeed.net/teams/eng_" + year + "_1.js";
    const promise = fetch(url)
        .then(response => { return response.text(); });
    return promise;
}

function getRaces() {
    const data = require('./TFeedUrls.json');
    for (var year in data) {
        const [page_urls, re] = [data[year], new RegExp(year + "/.+")];
        races[year] = [];
        for (var i in page_urls) {
            const url_end = re.exec(page_urls[i])[0];
            const race_name = url_end.split("/")[1];
            races[year].push(race_name);
        }
    }
}

function createUrl(year, race_name) {
    const base_url = "https://f1.tfeed.net/sessions/";
    const js_url = base_url + year + "_" + race_name + "/session.js";
    return js_url;
}

async function getZipContent(year, race_name) {
    const dt_path = './DriverTables/' + year + '_' + race_name + '.json';
    fs.readFile(dt_path, 'utf8', (errorx, datax) => {
        if (errorx) { console.error(errorx); }
        ntDriversTable = JSON.parse(datax);
        let [zip_counter, n] = [0, 30];
        const zip_file = "./ZipFiles/" + year + "_" + race_name + ".zip";
        const tt_folder = './Timetables/' + year + '_' + race_name;
        fs.mkdir(tt_folder, (errory) => { });
        // read the zip file and loop through the .js files in the zip
        fs.readFile(zip_file, function (error, data) {
            if (error) { console.error(error); }
            JSZip.loadAsync(data).then(async function (zip) {
                for (var fn in zip.files) {
                    // get the content of the zip files in string format
                    const content = await zip.files[fn]
                        .async('string');
                    eval(content);
                    if (timetable != {}) {
                        const tt_counter = (zip_counter / n) + 1;
                        const tt_filename = tt_folder + '/timetable_' + tt_counter.toString() + '.json';
                        // only save the data from 1 out of 30 zip files
                        // to prevent data overload
                        if (isDivisible(zip_counter, n)) {
                            fs.writeFile(tt_filename,
                                JSON.stringify(timetable), error => {
                                    if (error) { console.error(error); }
                                });
                        }
                        zip_counter++;
                    }
                }
            })
        })
    })
}

function createFolder(year, race_name) {
    // create a folder for the involved event
    const year_folder = './RaceData/' + year;
    mkdir(year_folder, (error) => { });
    const race_folder = year_folder + '/' + race_name;
    mkdir(race_folder, (error) => { });
    return race_folder;
}

async function saveSeasonInfo(year) {
    const year_folder = './RaceData/' + year;
    var [version, valid] = [1, true];
    while (valid) {
        var driver_script = '';
        try {
            driver_script = await fetchDrivers(year, version);
            eval(driver_script);
            const drivers_json = JSON.stringify(
                Object.assign({}, drivers));
            fs.writeFile(year_folder + '/drivers_'
                + version.toString() + '.json',
                drivers_json, error => {
                    if (error) { console.error(error) };
                });
            version++;
        } catch { SyntaxError } { valid = false; }
    }
    const teams_script = await fetchTeams(year);
    eval(teams_script);
    const teams_json = JSON.stringify(Object.assign({}, teams));
    fs.writeFile(year_folder + '/teams.json',
        teams_json, error => { if (error) { console.error(error) }; });
}

function getSessionHistory(history) {
    const new_history = {};
    for (var driver in history) {
        new_history[driver] = {};
        for (var lap in history[driver]) {
            new_history[driver][lap] = {};
            ndh = new_history[driver][lap];
            dh = history[driver][lap];
            ndh['position'] = dh[0];
            ndh['lap_time'] = dh[1];
            ndh['gap_to_leader'] = dh[2];
            ndh['interval'] = dh[3];
            ndh['nr_pitstops'] = dh[5];
            ndh['pit_status'] = dh[7];
            ndh['sector1'] = dh[11];
            ndh['sector2'] = dh[12];
            ndh['sector3'] = dh[13];
            ndh['prev_driver'] = dh[14];
            new_history[driver][lap] = ndh;
        }
    }
    return new_history;
}

function loadZips(year, race_name) {
    const url = "https://f1.tfeed.net/sessions/" + year + "_" + race_name + "/session.zip"
    var file = fs.createWriteStream('./ZipFiles/' + year + "_" + race_name + ".zip");
    http.get(url, function (response) {
        response.pipe(file);
        file.on('finish', function () { file.close(); });
    });
}

async function saveDriverTables(year, race_name) {
    const js_url = createUrl(year, race_name);
    const ndd_script = await fetchNddScript(js_url);
    eval(ndd_script);
    const fn = './DriverTables/' + year + '_' + race_name + '.json';
    fs.writeFile(fn, JSON.stringify(ntDriversTable), error => {
        if (error) { console.error(error); }
    });
}

async function loadData() {
    getRaces();
    var p_nt = ntDriversTable;
    for (var j = 2023; j < 2024; j++) {
        const year = j.toString();
        const races_y = races[year];
        for (var k = 0; k < races_y.length; k++) {
            const race_name = races_y[k];
            console.log(year, race_name);
            // saveDriverTables(year, race_name);
            getZipContent(year, race_name);
            await new Promise((resolve, reject) => setTimeout(() => resolve(true), 10000));
            continue;
        }
    }
}

async function main() {
    try { loadData(); }
    catch (error) { console.error(error); }
}

main();