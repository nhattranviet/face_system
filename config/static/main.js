$(document).ready(function () {
    var array=[];
    let namespace = "/test";
    var dataURL="";
    var counter=1;
    //Task socket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function () {
        console.log('Connected!');
    });

    socket.on('outImage', function (data) {
        console.log(data);
    });
    
    
    $("#test").on('click', function(){        
        // extractFrames();
        $("img#bg").attr("src","/video_feed");
        // setTimeout(function(){ $("img#bg").attr("src","/video_feed");}, 30000);
        
    });
    
    document.querySelector('input').addEventListener('change', extractFrames, true);

    function extractFrames() {
        
        var video = document.createElement('video');
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var pro = document.querySelector('#progress');
        function initCanvas(e) {
            canvas.width = this.videoWidth;
            canvas.height = this.videoHeight;
            
        }

        function drawFrame(e) {
            this.pause();
            ctx.drawImage(this, 0, 0);
            
            //send to server
            dataURL = canvas.toDataURL('image/jpeg');
            socket.emit('input image', dataURL,counter);
            counter++;
            //save to dict

            pro.innerHTML = ((this.currentTime / this.duration) * 100).toFixed(2) + ' %';
            if (this.currentTime < this.duration) {
                this.play();
            }
        }

        function saveFrame(blob) {

            let bl=URL.createObjectURL(blob);
            console.log(bl+"===>"+ counter);
            // let chk=bl.split('/')
            // if(chk[chk.length-1]=="undefine"){
            //     console.log("undefined with counter= "+counter);
            //     bl="default";
            // }
            array[counter]=bl;
        }

        function revokeURL(e) {
            URL.revokeObjectURL(this.src);
        }

        function onend(e) {
            // var img = document.getElementById("photo");
            // // do whatever with the frames
            // for (var i = 0; i < array.length; i++) {
            //     let obj = URL.createObjectURL(array[i])
            //     photo.setAttribute('src', obj);
            //     console.log(obj);
            // }
            // // we don't need the video's objectURL anymore
            // URL.revokeObjectURL(this.src);
            // console.log(array.length);
        }

        video.muted = true;
        video.addEventListener('loadedmetadata', initCanvas, true);
        video.addEventListener('timeupdate', drawFrame, true);
        video.addEventListener('ended', onend, true);

        video.src = URL.createObjectURL($("#uplFile").prop('files')[0]);
        video.play();
    }
});

