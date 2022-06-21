function toggleVisible(id) {
    obj = document.getElementById(id)
    if (obj.type == "password")  obj.type = "text"
    else if (obj.type == "text") obj.type = "password"
    return false
}
