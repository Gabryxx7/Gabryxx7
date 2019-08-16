---
layout: photos
title: Photos
include:
    js:
        - /assets/gabryxx7/js/instafeed.min.js
    # css: 
    #     - /assets/gabryxx7/css/lato.css 
---
 <div class="columns"><div id="instafeed"></div></div>

<script type="text/javascript">
    $("#instafeed").attr("test","ciao");
    var feed = new Instafeed({
        target: 'instafeed',
        get: 'user',
        sortBy: 'most-recent',
        resolution: 'standard_resolution',
        userId: '{{ site.instagram.user_id }}',
        accessToken: '{{ site.instagram.access_token }}',
        clientId: '{{ site.instagram.client_id }}',
        limit: '100',
        {% raw %}template: "<div class='column column-1-2'><article class='project-card' style='margin-bottom: 0; padding-bottom: 0;'> <a href='{{link}}' class='no-hover no-print-link flip-project'> <div class='project-card-img img'><img data-ignore src='{{image}}'> </img></div></a><p class='project-card-text' style='font-size: .7em; line-height: 1.4em;'>{{caption}}</p></article></div>",{% endraw %}
        success: function(response){
                    console.log("Instafeed.js response", response);
                }
    });
    feed.run();
</script>