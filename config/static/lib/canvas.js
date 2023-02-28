var c = document.getElementById("canvas");
var ctx = c.getContext("2d");
var img = document.getElementById("scream_temp");
//ctx.drawImage(img,0,0);
var preX;

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
            break;
        }
    }
}

function Notice() {
    alert(" Đã cắt vùng xử lý xong!");
}
(function($) {

    var preX;
    var preY;
    var tool; // pen, line
    var canvas;
    var context;
    var imageData;
    var paint;
    var listPoinX = new Array();
    var listPoinY = new Array();
    var listLineX = new Array();
    var listLineY = new Array();
    var diem1 = new Array();
    var diem2 = new Array();
    var diem3 = new Array();
    var diem4 = new Array();
    var listResultX = new Array();
    var listResultY = new Array();
    var Rdiem1 = new Array();
    var Rdiem4 = new Array();
    var listPoint = new Array();
    $.fn.makeDrawable = function() {

        canvas = this[0];
        if (!$(canvas).is("canvas"))
            throw "The target element must be a canvas";

        context = canvas.getContext("2d");

        if (tool == "demo") {
            var listDemoX = [171, 271, 220, 176, 171];
            var listDemoY = [47, 51, 104, 97, 47];
            for (var i = 0; i++; i < listDemoX.length) {
                context.fillStyle = "#ffbb33";
                context.beginPath();
                context.arc(listDemoX[i], listDemoY[i], 5, 0, 2 * Math.PI);
                context.fill();

            }
        }
        $(canvas).mousedown(function(e) {
            preX = e.pageX - canvas.offsetLeft;
            preY = e.pageY - canvas.offsetTop;
            paint = true;
            var temp = [1, 2];
            if (tool == "line") {
                imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            }
            if (tool == "draw") {

                imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                listPoinX.push(preX);
                listPoinY.push(preY);
                temp[0] = preX;
                temp[1] = preY;
                listPoint.push(temp);
                context.fillStyle = "#ffbb33";
                context.beginPath();
                context.arc(preX, preY, 5, 0, 2 * Math.PI);
                context.fill();
                if (listPoinX.length > 1) {



                    if (listPoinX[0] <= preX + 5 && listPoinX[0] >= preX - 5 && listPoinY[0] <= preY + 5 && listPoinY[0] >= preY - 5) {
                        context.moveTo(listPoinX[listPoinX.length - 2], listPoinY[listPoinY.length - 2]);
                        context.lineTo(listPoinX[listPoinX.length - 1], listPoinY[listPoinY.length - 1]);
                        context.stroke();

                        listPoinX.pop()
                        listPoinY.pop();
                        console.log(listPoinX);
                        console.log(listPoinY);
                        listResultX.push(...listPoinX);
                        listResultY.push(...listPoinY);
                        setTimeout(Notice, 1000);
                        listPoinX.splice(0, listPoinX.length);
                        listPoinY.splice(0, listPoinY.length);

                    } else {
                        context.moveTo(listPoinX[listPoinX.length - 2], listPoinY[listPoinY.length - 2]);
                        context.lineTo(listPoinX[listPoinX.length - 1], listPoinY[listPoinY.length - 1]);
                        context.stroke();
                    }
                }


            }


        });
        $(canvas).mousemove(function(e) {
            if (paint) {
                var x = e.pageX - canvas.offsetLeft;
                var y = e.pageY - canvas.offsetTop;

                if (tool == "pen") {
                    // $("#canvas").clear();

                    context.moveTo(preX, preY);
                    context.lineTo(x, y);
                    context.stroke();

                    preX = x;
                    preY = y;
                } else if (tool == "line") {
                    $("#canvas").clear();
                    canvas.width = canvas.width; // clear canvas content
                    // context.putImageData(imageData,0,0);

                    // context.moveTo(preX,preY);
                    // context.lineTo(x,x);
                    // context.stroke();
                    ctx.drawImage(img, 0, 0);
                    context.moveTo(preX, preY);
                    context.lineTo(x, preY);
                    context.stroke();

                    context.moveTo(preX, preY);
                    context.lineTo(preX, y);
                    context.stroke();

                    context.moveTo(x, preY);
                    context.lineTo(x, y);
                    context.stroke();

                    context.moveTo(preX, y);
                    context.lineTo(x, y);
                    context.stroke();
                    //console.log(x);
                    // console.log(y);
                    listLineY.push(y);
                    listLineX.push(x);

                } else if (tool == "draw") {
                    $("#canvas").clear();
                    canvas.width = canvas.width; // clear canvas content
                    context.putImageData(imageData, 0, 0);

                    // context.moveTo(preX,preY);
                    // context.lineTo(x,y);
                    // context.stroke();

                }

            }
        });

        $(canvas).mouseup(function(e) {
            if (tool == "line") {
                var x = e.pageX - canvas.offsetLeft;
                var y = e.pageY - canvas.offsetTop;

                diem1.push(preX);
                diem1.push(preY);
                diem2.push(listLineX[listLineX.length - 1]);
                diem2.push(preY);
                diem3.push(preX);
                diem3.push(listLineY[listLineY.length - 1]);
                diem4.push(listLineX[listLineX.length - 1]);
                diem4.push(listLineY[listLineY.length - 1]);
                console.log(diem1);
                console.log(diem2);
                console.log(diem3);
                console.log(diem4);
                Rdiem1.push(...diem1);
                Rdiem4.push(...diem4);
                diem1.splice(0, diem1.length);
                diem2.splice(0, diem2.length);
                diem3.splice(0, diem3.length);
                diem4.splice(0, diem4.length);
                // context.moveTo(preX,preY);
                // context.lineTo(x,y);
                // context.stroke();

            } else if (tool == "draw") {

            }
            paint = false;
        });
        $(canvas).mouseleave(function(e) {
            paint = false;
        });

        return $(canvas);
    };

    $.fn.setTool = function(newTool) {
        tool = newTool;
        return $(canvas);
    }
    $.fn.clear = function() {
        canvas.width = canvas.width;
        return $(canvas);
    }


    function popT() {
        temp.pop();
        temp.pop();
    }

    // function popAll() {
    //     roi_para_ls.slice(0, roi_para_ls.length);
    //     crop_para.slice(0, crop_para.length);
    // }
    $("#btnProcess").on('click', function() {
        let streamText = $("#streamText").val();
        let crop_para = new Array();


        crop_para.push(Rdiem1);
        crop_para.push(Rdiem4);


        let roi_para_ls = new Array();

        roi_para_ls.push(...listPoint);
        roi_para_ls.pop();

        $.ajax({
            url: '/sendROI',
            type: 'POST',
            data: JSON.stringify({
                crop_para: crop_para,
                roi_para_ls: roi_para_ls,
                streamText: streamText
            }),
            contentType: "application/json; charset=utf-8",
            success: function(res) {
                $("#scream_temp").css("display", "block");
                $("#canvasROI").css("display", "none");
                $("#scream_temp").attr("src", "/detect");
                $("#process").hide();
                $("#btnSubmit").css("display", "none");
                $("#btnReload").css("display", "block");

            }
        })

    });
    $("#btnReload").on('click', function() {
        roi_para_ls.slice(0, roi_para_ls.length);
        crop_para.slice(0, crop_para.length);
        $("#btnSubmit").css("display", "block");
        $("btnReload").css("display", "none");


    });
})(jQuery);

$(function() {

    $("#canvas").makeDrawable();
    $("#button1").click(function() {
        $("#canvas").clear();

    });

    $("#pen").change(function() {
        if (this.value) {
            $("#canvas").setTool("pen");

        }

    });
    $("#line").change(function() {
        if (this.value) {
            $("#canvas").setTool("line");

        }

    });
    $("#draw").change(function() {
        if (this.value)
            $("#canvas").setTool("draw");
    });
    $("#demo").change(function() {
        if (this.value)
            $("#canvas").setTool("demo");
    });
    $("#canvas").setTool("pen");
});