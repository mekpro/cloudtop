<html>
<head>
<style type="text/css">
  .container {
    width: 480px;
    height: 320px;
    margin: 4px auto; 
  }
</style>
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
<h2>CPU Time</h2>
<div id="graph_host_cputime" class="container"> </div>
<h2>Memory</h2>
<div id="graph_host_memory" class="container"> </div>

<script>
  result = rpc('get_host_stats', ['{{start}}','{{end}}','{{hostname}}']);
  document.write(result.info.hostname);

</script>
</p>

</body>
<script type="text/javascript" src="/static/flotr2.min.js">
<script type="text/javascript" src="/static/jquery.js">
</html>
