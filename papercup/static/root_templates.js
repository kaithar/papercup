
fullpage = `
<div>
  <div id="header">
    <div class="linkbox">
      <div id="mainnav">
        <router-link v-for="link in modulemenu" v-bind:href="link.href">{{link.text}}</router-link>
        <router-link href="/console/logout">Logout</router-link>
      </div>
      <div id="subnav">
        <router-link v-for="link in mainmenu" v-bind:href="link.href">{{link.text}}</router-link>
      </div>
    </div>
    <div style="position:absolute;top:5px;right:5px"><a href='#' @click.prevent="websock">{{websockstate}}</a></div>
  </div>
  <div id="sub_menu">
    <router-link v-for="link in submenu" v-bind:href="link.href">{{link.text}}</router-link>
  </div>
  <div id="td_content">
    <component v-bind:is="currentView"></component>
  </div>
  <vs-notify group="basic"></vs-notify>
  <component v-for="global_bit in global_components" v-bind:is="global_bit"></component>
  <div id="footer" class="footer">
    <component v-for="footer_bit in footer_components" v-bind:is="footer_bit"></component>
  </div>
</div>
`;


maintemplate = `<div id="main-section">
      <div class="title"><slot name="section-title">Loading...</slot></div>
      <div class="secmenu"><slot name="section-menu"></slot></div>
      <div id="content" class="content">
        <slot>Loading...</slot>
      </div>
    </div>`;
