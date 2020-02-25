/**
*
*  Base64 encode / decode
*  http://www.webtoolkit.info/
*
**/
var Base64 = {

  // private property
  _keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",

  // public method for encoding
  encode : function (input) {
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;

    input = Base64._utf8_encode(input);

    while (i < input.length) {

      chr1 = input.charCodeAt(i++);
      chr2 = input.charCodeAt(i++);
      chr3 = input.charCodeAt(i++);

      enc1 = chr1 >> 2;
      enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
      enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
      enc4 = chr3 & 63;

      if (isNaN(chr2)) {
        enc3 = enc4 = 64;
      } else if (isNaN(chr3)) {
        enc4 = 64;
      }

      output = output +
      this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
      this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);

    }

    return output;
  },

  // public method for decoding
  decode : function (input) {
    var output = "";
    var chr1, chr2, chr3;
    var enc1, enc2, enc3, enc4;
    var i = 0;

    input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

    while (i < input.length) {

      enc1 = this._keyStr.indexOf(input.charAt(i++));
      enc2 = this._keyStr.indexOf(input.charAt(i++));
      enc3 = this._keyStr.indexOf(input.charAt(i++));
      enc4 = this._keyStr.indexOf(input.charAt(i++));

      chr1 = (enc1 << 2) | (enc2 >> 4);
      chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
      chr3 = ((enc3 & 3) << 6) | enc4;

      output = output + String.fromCharCode(chr1);

      if (enc3 != 64) {
        output = output + String.fromCharCode(chr2);
      }
      if (enc4 != 64) {
        output = output + String.fromCharCode(chr3);
      }

    }

    output = Base64._utf8_decode(output);

    return output;

  },

  // private method for UTF-8 encoding
  _utf8_encode : function (string) {
    string = string.replace(/\r\n/g,"\n");
    var utftext = "";

    for (var n = 0; n < string.length; n++) {

      var c = string.charCodeAt(n);

      if (c < 128) {
        utftext += String.fromCharCode(c);
      }
      else if((c > 127) && (c < 2048)) {
        utftext += String.fromCharCode((c >> 6) | 192);
        utftext += String.fromCharCode((c & 63) | 128);
      }
      else {
        utftext += String.fromCharCode((c >> 12) | 224);
        utftext += String.fromCharCode(((c >> 6) & 63) | 128);
        utftext += String.fromCharCode((c & 63) | 128);
      }

    }

    return utftext;
  },

  // private method for UTF-8 decoding
  _utf8_decode : function (utftext) {
    var string = "";
    var i = 0;
    var c = c1 = c2 = 0;

    while ( i < utftext.length ) {

      c = utftext.charCodeAt(i);

      if (c < 128) {
        string += String.fromCharCode(c);
        i++;
      }
      else if((c > 191) && (c < 224)) {
        c2 = utftext.charCodeAt(i+1);
        string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
        i += 2;
      }
      else {
        c2 = utftext.charCodeAt(i+1);
        c3 = utftext.charCodeAt(i+2);
        string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
        i += 3;
      }

    }

    return string;
  }

}

function make_basic_auth(user, password) {
  var tok = user + ':' + password;
  var hash = Base64.encode(tok);
  return "Basic " + hash;
}

$( function() {

  // Set the DatePicker minimum date
  datepicker.min = new Date().toISOString().split("T")[0];

  // Autocompletion that request SNCF API on user input and set the value of hidden input when user select from the autocompletion list
  $( "#trainfrom, #trainto" ).autocomplete({
    source: function( request, response ) { $.ajax({
      url : "http://api.navitia.io/v1/coverage/sncf/pt_objects?q=" + request.term ,
      method : 'GET',
      beforeSend : function(req) {
        req.setRequestHeader('Authorization', make_basic_auth('ac20e3f0-10a2-4f4e-a433-ca6b9f0cebdb',''));
      },
      success : function(result){
        var list = [];
        result.pt_objects.forEach((item, i) => {
          if(item.embedded_type == "stop_area"){
            list.push(item);
          }
        });
        response(list);
      }
    })},
    select : function(event,data){
      var target = ($(this).attr('id') == "trainfrom") ? "#fromdata" : "#todata";
      $(this).val(data.item.name);
      $(target).val(JSON.stringify(data.item));
      return false;
    },
    minLength : 2,
    autoFocus : true,
    create: function () {
                $(this).data('ui-autocomplete')._renderItem = function( ul, item ) {
                  return $( "<li>" )
                  .append( "<div>" + item.name  + "</div>" )
                  .appendTo( ul );
                };
  }
});

  // Set the form readonly when user typed more than 3 char
  $( "#trainfrom, #trainto" ).bind( 'input', function(){
    if($(this).val().length > 3){
      $(this).prop( "readonly", true );
    }
  });

  // Reinitialization of the corresponding form when the the user click one of the cross buttons
  $( "#reinit-from, #reinit-to" ).click( function() {
    var target = ($(this).attr('id') == "reinit-from") ? "#trainfrom" : "#trainto";
    $(target).prop( "readonly", false );
    $(target).val('');
  });

// Set a default clockpicker
  $('.clockpicker').clockpicker();
});
