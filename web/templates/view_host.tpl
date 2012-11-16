%include templates/header 
<script>
  h = rpc('get_host_stats', ['{{start}}','{{end}}','{{hostname}}']);
  console.log(h)

</script>
<div class="container-fluid">
  <h1>{{pagename}}</h1>
  <p>Last Update: {{dt}}</p>
  <div> 
    <ul>
      <li>Hostname: h.info.hostname</li>
      <li>CPU Core: h.info.cpus</li>
      <li>Running VM: h.info.doms_count</li>
    </ul>

  </div>

</div>

%include templates/footer
