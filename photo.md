---
layout: photo-feed
title: Photo Gallery
grouped: true
addons: [comments, about]
---

<div class="message" style="padding-left: 0.5rem;">
    I'm an amateur photographer who enjoys taking mostly landscape photos!
    <br/>
    <strong>My current gear (updated 2022): </strong>
    
    <div class="row" style="font-size: 0.75rem; line-height: 0.8rem;">
    <div class="col-md-6">
    <h3 style="margin: 0.25rem;"> Main </h3>
    <ul>
        <li><strong>Camera:</strong> Sony a7r III</li>
        <li><strong>Cover:</strong> Silicone Camera Protect Body for Sony A7 III</li>
        <li><strong>SD cards:</strong> MicroSD SanDisk Extreme PRO 256gb, Samsung 256gb Evo Plus MicroSD</li>
        <li><strong>Filters:</strong> NiSi V5 Pro Kit 100mm with CPL + Nisi 100x100mm Nano IR Neutral Density Filter - ND1000</li>
        <li><strong>Lenses:</strong> Tamron 17-28mm f2.8, Tamron 28-75mm f2.8, Sony 70-200mm f2.8 g-master</li>
        <li><strong>Lens </strong>Cleaning kit: UES DSLR Camera Sensor and Lens Cleaning Travel Kit</li>
        <li><strong>Tripod:</strong>Joby Gorillapod 3K + Manfrotto Element Traveller Tripod Small with Ball Head</li>
        <li><strong>Intervalometer:</strong> Photoolex T720N Wireless/Wired</li>
        <li><strong>Backpacks:</strong> Osprey Farpoint 40L, Lenovo Business Casual 17-inch Backpack</li>
        <li><strong>External </strong>Storage: Samsung T7 2TB + WD Passport 4tb USB-C</li>
    </ul>
    </div>
    <div class="col-md-6">
    <h3 style="margin: 0.25rem;"> Aerial </h3>
    <ul>
        <li><strong>Drone:</strong> Mavic Air 2 Fly More Combo</li>
        <li><strong>MicroSd:</strong> Samsung 128gb Evo Plus</li>
        <li><strong>Filter:</strong> Freewell Circular Polarizer (CPL) Filter for Mavic Air 2</li>
        <li><strong>Extra:</strong> 3 in 1 Car Charger Dual Battery Charger with USB Port for DJI Mavic Air 2 Drone</li>
    </ul>
    <h3 style="margin: 0.25rem;"> Others </h3>
    <ul>
        <li><strong>Phone:</strong> Galaxy S20 Plus Snapdragon</li>
        <li><strong>Action </strong>camera: GoPro Hero9 Black</li>
        <li><strong>Cover:</strong> Silicone cover with strap</li>
    </ul>
    </div>
</div>
</div>



<div class="photo-feed">

{% assign years = "" %}
{% assign photolist = site.data.photos-list %}
{% assign photo_sorted = site.data.photos-list.photos | sort:"timestamp" | reverse %}
{% assign prev_year = 0 %}
{% assign extra_class = "" %}
{% assign mini_cnt = 0 %}

{% for photo in photo_sorted %}
    {% assign current_year = photo.timestamp | date:"%Y" %}
    {% if page.grouped %}
        {% if current_year != prev_year %}
            {% assign prev_year = current_year %}
            <div class="year-break"> 
            <h1 id="{{ current_year }}"> {{ current_year }}  <span class="posts-year-count"> </span> </h1>
            {% assign years = years | append: "," | append: current_year %}
            <!-- <blockquote class="photo-group-date-container">
                <div class="photo-group-date">
                </div>
            </blockquote> -->
            </div>
        {% endif %}
    {% endif %}
    {% if photo.file.size < 2 %}
        {% if mini_cnt == 1 %}
            {% assign mini_cnt = 2 %}
            {% assign extra_class = "mini" %}
        {% else %}
            {% assign mini_cnt = 0 %}
            {% assign min = 1 %}
            {% assign max = 100 %}
            {% assign diff = max | minus: min %}
            {% assign randomNumber = "now" | date: "%N" | modulo: diff | plus: min %}
            {% if randomNumber > 0 and randomNumber <= 30 %}
                {% assign extra_class = "mini" %}
                {% assign mini_cnt = 1 %}
            {% elsif randomNumber > 30 and randomNumber <= 85 %}
                {% assign extra_class = "" %}
            {% else %}
                {% assign extra_class = "highlight" %}
            {% endif %}
        {% endif %}
        {% if photolist.highlights_timestamps contains photo.timestamp %}
            {% assign extra_class = "highlighted_timestamp" %}
            {% assign extra_style = "flex: 0 1 auto;" %}
        {% else %}
            {% assign extra_style = "" %}
        {% endif %}
    {% else %}
        {% assign mini_cnt = 3 %}
    {% endif %}
    {% include photo-card.html photo=photo extra_class=extra_class extra_style=extra_style %}
    {% assign prev_year = current_year %}
{% endfor %}   
</div>


{% assign years = years | remove_first: ',' | split: ',' %}
{% if years.size > 0 %}
<div class="photo-toc">
<ul class="toc-show" id="markdown-toc">
<li class="close-btn">&gt;</li>
{% for year in years %}
<li><a href="#{{ year }}" id="markdown-toc-{{ year }}" style="font-weight: bold;">{{ year }} <span class="posts-year-count"> </span></a></li>
{% endfor %}
</ul>
</div>

<script>
$(function(){
    $(".photo-toc .close-btn").click(function(event) {
        $(event.target).parent().parent().toggleClass("closed");
    });
    var counter = 0;
    var year = 0;
    var data = $(".photo-feed > *");
    $.each(data, function(index, value) {
        var isLastElement = index == data.length -1;
        if($(this).hasClass("year-break") || isLastElement){
            if(year > 0){
                console.log(year +" - " + counter);
                $("#"+year+" .posts-year-count").text(counter);
                $("#markdown-toc-"+year+" .posts-year-count").text(counter);
            }
            if(!isLastElement){
                year = $(this).find("h1")[0].childNodes[0].nodeValue.trim();
                counter = 0;
            }
        }
        counter++;
    });
});
</script>
{% endif %}
