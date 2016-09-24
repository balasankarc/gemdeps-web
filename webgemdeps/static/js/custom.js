function deleteConfirm(appname) {
    if (confirm('Do you want to delete ' + appname + '?')) {
        window.location.href = "/delete/" + appname;
    } else {
        return false;
    }
}
