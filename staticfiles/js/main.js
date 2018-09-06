var text = "";
var n = 0;
var a = "";
var b = "";
var channel = "";

document.getElementById('start_button').onclick = function () {
  var sender = $('#sender').val();
  var fee = $('#fee').val();
  var receiver = $('#receiver').val();
  var amount = $('#amount').val();
  var utx = "";
  var hashes = [];
  $.when(
    $.ajax({
      url: "{% url 'prepare_signature' %}",
      type: "POST",
      data: {'sender': sender, 'amount':amount, 'receiver':receiver, 'fee':fee},
      success: function (data){
	text += "[log] creating transaction: " + data.unsigned + "<br><br>";
	for (i = 0; i < data.hashes.length; i++) {
	  n = i+1;
	  text += "[log] hash #" + n.toString() + ": " +data.hashes[i] +  "<br>";
	}
	text += "<br>[log] homomorphic signature operation with murmur...<br>";
	document.getElementById('log').innerHTML = text;
	utx = data.unsigned;
	hashes = data.hashes;
      }
    })
  ).done(function(data){
    $.when(
      $.ajax({
	url: '{% url "sign" %}',
	type: "POST",
	data: {"name":"key", "pubkey":b, "hashes":data.hashes, "channel":channel},
	success: function(data){
	  text += "[log] signature complete!<br><br>";
	  document.getElementById('log').innerHTML = text;
	}
      })
    ).done(function(data){
      $.ajax({
	url: '{% url "push" %}',
	type: "POST",
	data: {"pubkey":b, "sigs": data.Content, "unsigned": utx},
	success: function(data){
	  text += "[log] txid: <a target='_blank' href='https://testnet.blockchain.info/tx/"+ data.txid+"'> "+data.txid+"</a><br>";
	  document.getElementById('log').innerHTML = text;
	}
      })
    });
  });
}

document.getElementById('create').onclick = function () {
  $.when(
    $.ajax({
      url: '{% url "newmurmur" %}',
      type: "POST",
      data: {"IdentityKey": "newId"},
      success: function (data){
	text += "[log] new murmur channel created: " + data.ChannelId + "<br>";
	text += "[log] storing private key...<br>";
	document.getElementById('log').innerHTML = text;
	channel = data.ChannelId;

      },
    }),
    $.ajax({
      url: "{% url 'get_testwallet' %}",
      success: function (data){
	text += "[log] new wallet created! <br>[log] address: " + data.address + "<br>";
	text += "[log] <a target='_blank' href='https://testnet.blockchain.info/address/"+data.address+"'> see here</a><br><br>";
	document.getElementById('log').innerHTML = text;
	$('#sender').val(data.address);
	$('#receiver').val("mfeVwF1taoNGJpT2ozRpuqpYqp37t42SMy");
	$('#amount').val("0.09999");
	$('#fee').val("0.00002");
	a = data.priv;
	b = data.pub;
      }
    })
  ).done(function (){
    $.ajax({
      url: '{% url "write" %}',
      type: "POST",
      data: {"key": a, "name": "key", "channel": channel},
      success: function(data){
	text += "[log] "+ data.status +" <br><br>";
	document.getElementById('log').innerHTML = text;
      }
    });			
  });
  $.ajax({
    url: "{% url 'fund_wallets' %}",
    success: function(data){
      console.log(data);
    }
  });
}
$.ajaxSetup({ 
  beforeSend: function(xhr, settings) {
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
	var cookies = document.cookie.split(';');
	for (var i = 0; i < cookies.length; i++) {
	  var cookie = jQuery.trim(cookies[i]);
	  // Does this cookie string begin with the name we want?
	  if (cookie.substring(0, name.length + 1) == (name + '=')) {
	    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	    break;
	  }
	}
      }
      return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      // Only send the token to relative URLs i.e. locally.
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
  } 
});
