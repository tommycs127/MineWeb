function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = () => {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.response);
    }
    xmlHttp.responseType = 'json';
    xmlHttp.open("GET", theUrl, true);
    xmlHttp.send(null);
}

function writeTable(res) {
    var t = document.getElementById('status');
        t.innerHTML = '';
    var r1 = t.insertRow(0);
    var r2 = t.insertRow(1);
    var h1 = r1.insertCell(0);
        h1.innerHTML = "<b>Status</b>";
    var d1 = r1.insertCell(1);
        d1.innerHTML = (res["online"] == "true")  ? "Online" :
                       (res["online"] == "false") ? "Offline" : "Unknown";
                   
    if (res["online"] == "true") {
        var h2 = r2.insertCell(0);
            h2.innerHTML = "<b>Version</b>";
        var d2 = r2.insertCell(1);
            d2.innerHTML = res["status"]["version"]["name"];
        
        var r3 = t.insertRow(2);
        var h3 = r3.insertCell(0);
            h3.innerHTML = "<b>Players</b>";
        var d3 = r3.insertCell(1);
            d3.innerHTML = res["status"]["players"]["online"] + ' / ' + res["status"]["players"]["max"];
    } else {
        var b2 = r2.insertCell(0);
            b2.innerHTML = `
                    <form action="/server/start">
                        <input type="submit" style="background-color: green; width: 100%; height: 100%" value="Switch On" />
                    </form>`;
            b2.colSpan = 2;
    }
}

function refresh() {
    httpGetAsync("/api/server", writeTable);
    refresh_button = document.getElementById("refresh")
    refresh_button.disabled = true;
    setInterval(() => { refresh_button.disabled = false; }, 5000);
}

window.onload = () => { refresh(); }