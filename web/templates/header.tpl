<html>
<head>
  <title> Cloudtop Web </title>
  <script src="/static/jquery.js"></script>
  <script src="/static/flotr2.min.js"></script>
  <link href="/static/css/bootstrap.min.css" rel="stylesheet" media="screen">
  <style type="text/css">
    body { 
      padding-top: 60px;
      padding-bottom: 40px;
    }
    .graph {
      width: 320px;
      height: 240px;
      margin: 8px auto;
    } 
    
    .minigraph {
      width: 180px;
      height: 120px;
    }
    
  </style>
</head>
<body>
  <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
        <a class="brand" href="#">CloudTopWeb</a> 
      <ul class="nav">
        <li class="active"><a href="#">Overview</a></li>
        <li><a href="#">Host</a></li>
        <li><a href="#">VM</a></li>
        <li><a href="#">Report</a></li>
      </ul>
      </div>
    </div>
  </div>
  <script>
  function new_request() {
      var req;
      req = new XMLHttpRequest();
      return req;
  }
  function rpc(method, params) {
      var i;
      var req = new_request();
      req.open('POST', '/rpc', false);
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
