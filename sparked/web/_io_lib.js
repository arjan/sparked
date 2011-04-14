(function()
{
    var clientId = "";
    var _feed = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (var i=0; i<32; i++)
    {
        clientId += _feed.charAt(Math.floor(Math.random()*_feed.length));
    }

    /*
     Provide the XMLHttpRequest constructor for IE 5.x-6.x:
     Other browsers (including IE 7.x-9.x) do not redefine
     XMLHttpRequest if it already exists.
     This example is based on findings at:
     http://blogs.msdn.com/xmlteam/archive/2006/10/23/using-the-right-version-of-msxml-in-internet-explorer.aspx
     */
    if (typeof XMLHttpRequest == "undefined")
        XMLHttpRequest = function () {
            try { return new ActiveXObject("Msxml2.XMLHTTP.6.0"); }
            catch (e) {}
            try { return new ActiveXObject("Msxml2.XMLHTTP.3.0"); }
            catch (e) {}
            try { return new ActiveXObject("Msxml2.XMLHTTP"); }
            catch (e) {}
            //Microsoft.XMLHTTP points to Msxml2.XMLHTTP.3.0 and is redundant
            throw new Error("This browser does not support XMLHttpRequest.");
        };
    function requestFactory(method, url)
    {
        var r = new XMLHttpRequest();
        r.open(method, url, true);
        r.setRequestHeader("X-IO-ClientID", clientId);
        return r;
    }

    function encodeMessage (input)
    {
        return input;
    }

    function decodeMessage (input)
    {
        return input;
    }

    var currentPoll = null;
    var messageQueue = [];

    var receiveFunction = function(msg)
    {
        console.log("sparked.web.io: Message received", msg);
    };

    function sendMessage(msg)
    {
        var req = requestFactory("POST","/sparked.web.io/send");
        req.send(encodeMessage(msg));
    }

    function doPoll(msg)
    {
        if (currentPoll)
        {
            currentPoll.abort();
        }
        currentPoll = requestFactory("POST","/sparked.web.io/recv");
        var req = currentPoll;
        req.onreadystatechange = function() {
            if (req.readyState == 4)
            {
                if (req.status != 200)
                {
                    console.log('error!');
                    
                    return;
                }
                receiveFunction(decodeMessage(req.responseText));
                currentPoll = null;
                doPoll();
            }
        };
        req.send(msg);
    }

    // The global entry points
    window.IO = {
        send: sendMessage,
        recv: function (cb) {
            receiveFunction = cb;
        }
    };

    function startPolling ()
    {
        setTimeout(doPoll, 100);
    }

    // Start the poll
    if(document.addEventListener)
    {
        document.addEventListener('load',startPolling, true); //W3C
    }
    else
    {
        document.attachEvent('onload',startPolling); //IE
    }

})();


