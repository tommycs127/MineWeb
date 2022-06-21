function replaceLink(id, type) {
    var links = document.getElementById(id).getElementsByTagName('a');
    for (var i=0; i<links.length; i++) {
        if (!links[i].href.match(/\#/g)) {            
            if (type == 'edit')
                links[i].href = links[i].href.replace('edit', 'read');
            else if (type == 'add')
                links[i].href = links[i].href.replace('wiki', 'wiki/read');
            else if (type == 'history_read')
                links[i].href = links[i].href.replace('wiki/history', 'wiki');
            links[i].target = "_blank";
        }
    }
}

function addLink(id) {
    for (var header of ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) {
        h = document.getElementById(id).getElementsByTagName(header);
        for (var e of h)
            e.id = e.innerText.replace(/\ /g, '_');
    }
}