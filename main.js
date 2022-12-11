

            function showImg(imgSrc, H, W, Caption) {
            var newImg = window.open("","myImg",config="height="+H+",width="+W+"")
            newImg.document.write("<title>"+ Caption +"</title>")
            newImg.document.write("<img src='"+ imgSrc +"' height='"+ H +"' width='"+ W +"' onclick='window.close()' style='position:absolute;left:0;top:0'>")
            newImg.document.write("<script type='text/javascript'> document.oncontextmenu = new Function(\"return false\") </sc"+"ript>")
            newImg.document.close()
            }