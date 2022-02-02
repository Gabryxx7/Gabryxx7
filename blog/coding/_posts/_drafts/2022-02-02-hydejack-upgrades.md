---
title: Hydejack Upgrades
excerpt_separator: <!--more-->
image: 
  path: /home/gabryxx7/repos/blog/assets/img/blog/hydejack-9.jpg
#   class: "wide-img"
---

# CSS only submenu
Create a new file `/#jekyll-theme-hydejack/_includes/body/sub-menu.html`

```liquid
{% assign menu = include.menu %}
{% for node in menu %}
    {% assign url = node.url | default: node.href %}
    <li {% if node.menu.size > 0 %} class="has_submenu" {% endif %}>
        <a
        {% if forloop.first %}id="_drawer--opened"{% endif %}
        {% if node.url %}href="{% include_cached smart-url url=url %}"{% endif %}        
        class="sidebar-nav-item {% if node.external  %}external{% endif %}"
        {% if node.rel %}rel="{{ node.rel }}"{% endif %}
    >
        {{ node.name | default:node.title }}
    </a>
    {% if node.menu %}
        <ul class="sub-menu">
            {% include body/sub-menu.html menu=node.menu %}   
        </ul>     
    {% endif %}
    </li>
{% endfor %}
```

Edit `/#jekyll-theme-hydejack/_includes/body/nav.html` and replace the content of this `if` statement with this:
```liquid
  {% if site.menu %}
   {% include body/sub-menu.html menu=site.menu %}
  {% else %}
```

Add a new `sass` file `sub-menu.scss`:

```sass
.sub-menu{
    padding: 0;
    margin: 0;
    display: block;
    transition: max-height 0.3s ease-out, opacity 0.2s linear;
    max-height: 0rem;
    position: relative;
    margin-left: 0.5rem;
    list-style: none;
    overflow: hidden;
    opacity: 0;
    margin-left: 20%;
    a {
        font-size: 90%;
        margin-bottom: 0.2rem;
        font-weight: 100;
        line-height: 1.3;
        font-family: 'Noto Sans';
        text-decoration-thickness: 1px;
    }
  }
  
  /* Show the dropdown menu on hover */
  .has_submenu:hover > .sub-menu{
      transition: max-height 0.3s ease-out, opacity 0.2s linear;
      display: block;
      max-height: 10rem;
      opacity: 1;
  }

  .has_submenu > a::after{
    font-family: 'icomoon' !important;
    display: inline-block;
    position: absolute;
    content: "\ea29";
    margin-left: 1.5rem;
    margin-top: 0.7%;
    font-size: 90%;
    vertical-align: middle;
}

.sidebar-nav > ul > .has_submenu > .sub-menu{
    margin-left: -0.2rem;  
    margin-top: -0.1rem;
  } 

```

Import the new file adding this at the end of `my-style.scss`: 
```sass
@import "sub-menu";
```

Finally, add your submenu (and sub-submenus etc...) to your `_config.yml`:

```yaml

menu:
  - title:             Blog
    url:               /blog
  - title:             Photo Gallery
    url:               /photo/
    menu:
      - title:  test1
        url:    /photo/
      - title:  test2
        url:    /photo/
        menu:
        - title:  test21
          url:    /photo/
        - title:  test22
          url:    /photo/
  - title:             Résumé\CV
    url:               /resume/
  - title:             Publications
    url:               /resume/#publications
  - title:             Projects
    url:               /projects/
```

# Photo Gallery