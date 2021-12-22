var canvas;
var context;
var image = new Image();
var draggedCircle = null;
var draggedInitialPos = new Position(-1, -1);
var dragging = false;
var draggingThreshold = 10;
var touchesStart = 0;
var textxml = null;
var boltImage = new Image();
var boltXml = null;
//Cool trick, get the svg file, read it as an XML, replace its colors
$.get('../media/flash.svg', function(svgXml) {
    boltXml = svgXml.documentElement.outerHTML.replace('fillColor', "#fbff00").replace('strokeColor', "#727272");
    boltImage.src = "data:image/svg+xml;charset=utf-8,"+boltXml;
  });

function initializeCanvas() {
    // Register an event listener to call the resizeCanvas() function 
    // each time the window is resized.
    window.addEventListener('resize', resizeCanvas, false);
    // Draw canvas border for the first time.
    resizeCanvas();
}

// Display custom canvas. In this case it's a blue, 5 pixel 
// border that resizes along with the browser window.
function redraw() {
    if(context != undefined && context != null){
        context.strokeStyle = 'blue';
        context.lineWidth = '5';
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        //context.strokeRect(0, 0, window.innerWidth, window.innerHeight);

        // just being lazy so two cycles, one only draws elements whose deviceType is "Phone" the other only prints deviceType == "Beacon"
        // This is to make sure "Beacon" circles are drawn on top
        var toDraw = "Phone";
        for (var index = circles.length-1; index >= 0; index--) {
            if(circles[index].device != null && circles[index].device.deviceType == toDraw)
                circles[index].draw(context);
        }

        toDraw = "Beacon";
        for (var index = circles.length-1; index >= 0; index--) {
            if(circles[index].device != null && circles[index].device.deviceType == toDraw)
                circles[index].draw(context);
        }
    }
}

// Runs each time the DOM window resize event fires.
// Resets the canvas dimensions to match window,
// then draws the new borders accordingly.
function resizeCanvas() {
    canvas.width = image.width;
    canvas.height = image.height;
    redraw();
}

function newCircle(pos) {
    var cir = new Circle();
    cir.pos.x= pos.x;
    cir.pos.y= pos.y;
    cir.innerFill = defaultInnerFill;
    cir.innerSize = defaultInnerSize;
    cir.outerFill = defaultOuterFill;
    cir.outerSize = defaultOuterSize;
    cir.id = circles.length > 0 ? circles[circles.length - 1].id + 1 : 0;
    circles.push(cir);
    return cir;
}

function getCircle(id) {
    for (i in circles) {
        if (circles[i].id == id) {
            return circles[i];
        }
    }
}

function getMousePos(canvas, e) {
    var rect = canvas.getBoundingClientRect();
    var currentY = e.clientY;
    var currentX = e.clientX;
    if(e.originalEvent.touches){
        currentY = e.originalEvent.touches[0].clientY;
        currentX = e.originalEvent.touches[0].clientX;
    }
    return new Position(((currentX- rect.left) / (rect.right - rect.left) * canvas.width),
                        ((currentY - rect.top) / (rect.bottom - rect.top) * canvas.height));
}

function handleMouseDown(e) {
    var pos = getMousePos(canvas, e);
    draggedCircle = null;
    draggedInitialPos.x = -1;
    draggedInitialPos.y = -1;
    for (i in circles) {
        var inters = isIntersect(pos, circles[i]);
        if (inters > 0) {
            draggedCircle = circles[i];
            draggedInitialPos.x = circles[i].pos.x;
            draggedInitialPos.y = circles[i].pos.y;
            return;
        }
    }
}

function handleMouseUp(e) {
    if (dragging) {
        draggedCircle = null;
        draggedInitialPos.x = -1;
        draggedInitialPos.y = -1;
        dragging = false;
        return;
    }
    draggedCircle = null;
    draggedInitialPos.x = -1;
    draggedInitialPos.y = -1;
    dragging = false;
    var pos = getMousePos(canvas, e);
    var clickedIndex = -1;
    var clickedOrder = null;
    var clickedPrevSelection = null;
    for (i in circles) {
        var inters = isIntersect(pos, circles[i]);
        if (clickedIndex < 0 && inters > 0) {
            if (inters == 1) {
                console.log("Clicked " + circles[i].id + " inner!");
            }

            if (inters == 2) {
                console.log("Clicked " + circles[i].id + " outer!");
            }
            clickedIndex = i;
            clickedOrder = inters;
            clickedPrevSelection = circles[i].selected;
            circles[i].selected = true;
            console.log(getDeviceByNumber(circles[i].id));
        } else {
            circles[i].selected = false;
        }
    }

    $("#map-container .col").remove();
    if (clickedIndex >= 0) {
        if (clickedPrevSelection == true) {
            if(circles[clickedIndex].device == null){
                circles.splice(clickedIndex, 1);
            }
        }else{
            if(circles[clickedIndex].device != null && circles[clickedIndex].device.deviceType === "Phone"){
                var newDiv = circles[clickedIndex].device.divContainer.clone(true, true);
                newDiv.addClass("map");
                newDiv.prependTo($("#map-container"));
            }
        }
        redraw();
        return circles[clickedIndex];
    } else {
        var circle = newCircle(pos);
        redraw();
        return circle;
    }
    return 0;
}

function handleMouseMove(e) {
    if (draggedCircle != null) {
        var pos = getMousePos(canvas, e);
        if (!dragging) {
            if (Math.sqrt(((draggedInitialPos.x - pos.x) ** 2) + ((draggedInitialPos.y - pos.y) ** 2)) > draggingThreshold) {
                dragging = true;
            }
        }
        if (dragging && draggedCircle.device == null) {
            console.log("Dragging " + draggedCircle.id);
            draggedCircle.pos.x = pos.x;
            draggedCircle.pos.y = pos.y;
            redraw();
        }
    }
}


function isIntersect(point, circle) {
    var distFromCircleCenter = Math.sqrt((point.x - circle.pos.x) ** 2 + (point.y - circle.pos.y) ** 2);
    if (distFromCircleCenter < circle.innerSize)
        return 1;
    if (distFromCircleCenter < circle.outerSize)
        return 2;
    return 0;
}

$(function () {
    canvas = document.getElementById("canvas");
    context = canvas.getContext('2d');
    $(canvas).on('touchmove mousemove', function (e) {
        //If there is touch and the only one finger is touching and dragging the circle, then we prevent default
        //To avoid panning and scrolling with the touch, and we handle the circle
        if(e.originalEvent.touches){
            if(draggedCircle != null && e.originalEvent.touches.length == 1){
                e.preventDefault();
                e.originalEvent.preventDefault();
                handleMouseMove(e);    
            }
        }
        else{
            handleMouseMove(e);    
        }
    });

    $(canvas).on('mousedown touchstart', function (e) {
        if(e.originalEvent.touches){
            touchesStart = e.originalEvent.touches.length;
        }
        handleMouseDown(e);
    });

    $(canvas).on('mouseup touchend', function (e) {
        if(e.originalEvent.touches){
            if(touchesStart == 1){
                handleMouseUp(e);
            }
        }
        else{
            handleMouseUp(e);            
        }
    });

    image.onload = function () {
        resizeCanvas();
        //context.drawImage(image,0,0,canvas.width,canvas.height);
    };
    image.src = "media/background-map.png";

    initializeCanvas();
});
