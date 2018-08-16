
Vue.component('router-link', {
  template: `<a
    v-bind:href="href"
    v-bind:class="{ active: isActive }"
    v-on:click="go">
    <slot></slot>
  </a>`,
  props: { href: { type:String, required: true }},
  computed: { isActive () { return vm && this.href === vm.$data.currentURL } },
  methods: {
    go (event) {
      event.preventDefault()
      navigate_to(this.href)
    }
  }
})

Vue.component('maintemplate', {template: maintemplate})

var vm = new Vue({
  el: '#layout',
  template: fullpage,
  data: {
    currentView: 'maintemplate',
    modulemenu: [],
    mainmenu: [],
    submenu: [],
    global_components: [],
    footer_components: [],
    currentURL: '',
    websockstate: 'Websocket not connected.'
  },
  methods: {
    websock (event){
      if (vm.$data.websockstate == 'Websocket not connected.') {
        websock_connect()
      }
    }
  }
})

var routes = [
  {route: /^\/console\/?$/, load: ()=>{ vm.$data.currentView = 'maintemplate' }}
];

function navigate_to(url) {
  if (load_route(url))
    history.pushState(url,'',url)
  return false;  
}

function refresh_view() {
  load_route(history.state);
}

function back_one() {
  history.back()
}

function load_route(url) {
  console.log(url)
  for (var i = 0; i<routes.length; i++) {
    var t = routes[i].route.exec(url);
    if (t) {
      routes[i].load(t);
      if (routes[i].navigate === false) {
        return false
      }
      vm.$data.currentURL = t[0];
      return true;
    }
  }
  return false;
}

window.onpopstate = function (url) {
  load_route(url.state);
}

function websock_connect() {
  websocket = new WebSocket("wss://"+document.location.hostname+"/api/websock");
  websocket.onopen = function(evt) { onOpen(evt) };
  websocket.onclose = function(evt) { onClose(evt) };
  websocket.onmessage = function(evt) { onMessage(evt) };
  websocket.onerror = function(evt) { onError(evt) };  
}

document.onreadystatechange = function () {
    if (document.readyState === "interactive") {
      if (load_route(document.location.pathname))
        history.replaceState(document.location.pathname,'',document.location.pathname)
      websock_connect();
    }
}

function onOpen(evt)
{
  vm.$data.websockstate = 'Websocket connected'
  vm.$notify('basic', 'Websocket connected', '', 8000);
}

function onClose(evt)
{
  vm.$data.websockstate = 'Websocket not connected.'
  vm.$notify('basic', 'Websocket disconnected', 'warn', 8000);
}

function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

websock_types = {
  notification: function(data) {
    vm.$notify('basic', escapeHtml(data.data), '', 8000);
  }
}

function onMessage(evt)
{
  data = JSON.parse(evt.data);
  console.log(data)
  if (data.type in websock_types) {
    websock_types[data.type](data)
  }
}

function onError(evt)
{
  vm.$notify('basic', 'Websocket error!'+evt.data, 'error', 8000);
}

function doSend(message)
{
  websocket.send(JSON.stringify(message));
}
