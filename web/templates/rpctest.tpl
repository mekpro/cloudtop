<html>
<head>
<script>
function new_request() {
    var req;
    req = new XMLHttpRequest();
    return req;
}

// Simple blocking JSON-RPC function
function rpc(method, params) {
    var i;
    var req = new_request();
    req.open('POST', 'rpc', false);
    req.setRequestHeader('Content-Type', 'application/json');
    req.send(JSON.stringify({
        'method' : method,
        'params' : params,
        'id' : 1
    }));

    if(req.status == 200) {
        var ret = JSON.parse(req.responseText);

        if (ret.error !== null) {
            console.log(ret.error);
            return undefined;
        } else {
            return ret.result;
        }
    } else {
        return undefined;
    }
}
</script>
</head>
<body>

<p>
<script>
  document.write(rpc('get_host_stats', ['{{start}}','{{end}}','{{hostname}}']));
</script>
</p>

</body>
</html>
