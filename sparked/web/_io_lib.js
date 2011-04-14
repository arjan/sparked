/*
 * Sparked
 * -------
 * _io_lib.js part of sparked.web.io
 *
 * Copyright 2011 Arjan Scherpenisse <arjan@scherpenisse.net>
 *
 * Released under the MIT License
 */
(function()
{
    // Generate a client ID for all requests on this page
    var clientId = "";
    var _feed = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (var i=0; i<32; i++)
    {
        clientId += _feed.charAt(Math.floor(Math.random()*_feed.length));
    }

    if (!JSON || typeof JSON.stringify != 'function' || typeof JSON.parse != 'function') 
    {
        throw new Error("This browser does not support native JSON encoding/decoding.");
    }

    /* Provide the XMLHttpRequest constructor for IE 5.x-6.x: */
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
        return JSON.stringify(input);
    }

    function decodeMessage (input)
    {
        return JSON.parse(input);
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
