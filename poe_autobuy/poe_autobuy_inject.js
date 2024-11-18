function sleep(ms)
{
  return new Promise(resolve => setTimeout(resolve, ms));
}


var webSocket;
var ws_is_connected = false;
var data_id_list = ['', ''];
var selection_old = '';
var page_title = '';
var price_amount = '';
var price_type = '';

var filter_price_min_amount = 0;
var filter_price_max_amount = 0;
var filter_price_is_chaos = false;


function changeTitle()
{
	if (page_title == '' && !document.title.includes('Trade') && !document.title.includes('pathofexile'))
		page_title = document.title;
	
	if (page_title != '')
		document.title = page_title;
}

async function main()
{
	console.log('poe_autobuy start to inject');
	
	document.execCommand = function(execCommand)
	{
		return function(arguments)
		{
			if (arguments == 'copy')
			{
				var copy_text = document.activeElement.value.toString();
				copy_text = copy_text.replace(/"/g, '\\"');
				
				var message_data = '{"price_amount": "' + price_amount + '", "price_type": "' + price_type + '", "copy_text": "' + copy_text + '"}';
				console.log(message_data);
				
				if (ws_is_connected)
					webSocket.send('{"message_type": "trade", "message_data": ' + message_data + '}');
				
				price_amount = '';
				price_type = '';
			}
			//return execCommand(arguments);
			return null;
		}
	}(document.execCommand)
	
	
	webSocket = new WebSocket('ws://localhost:8000');
	ws_is_connected = false;
	
	webSocket.onopen = function()
	{
		ws_is_connected = true;
		console.log('WebSocket is open now.');
	};
	
	webSocket.onerror = function(event)
	{
		ws_is_connected = false;
		console.log('WebSocket error observed: ', event);
	};
	
	webSocket.onclose = function(event)
	{
		ws_is_connected = false;
		console.log('WebSocket is closed now: ', event);
	};
	
	while(!ws_is_connected)
	{
		await sleep(100);
	}

	console.log('poe_autobuy successfully injected');
	webSocket.send('{"message_type": "log", "message_data": "[WS] poe_autobuy successfully injected"}');
	
	
	
	
	
	
	
	
	// todo add overprice check
	

	var element_filter_property_list = document.getElementsByClassName('filter filter-property full-span');
	if (element_filter_property_list.length > 0)
	{
		for (var i = 0; i < element_filter_property_list.length; i++)
		{
			if (!element_filter_property_list[i].outerHTML.includes('Buyout Price'))
				continue;
			
			var element_input_list = element_filter_property_list[i].getElementsByTagName('input');
			if (element_input_list.length <= 0)
				continue;
			
			for (var n = 0; n < element_input_list.length; n++)
			{
				if (!element_input_list[n].hasAttribute('placeholder'))
					continue;
				
				if (element_input_list[n].getAttribute('placeholder') == 'min')
					filter_price_min_amount = parseInt(element_input_list[n].value) || 1;
				
				if (element_input_list[n].getAttribute('placeholder') == 'max')
					filter_price_max_amount = parseInt(element_input_list[n].value) || 10000;
				
				if (element_input_list[n].getAttribute('placeholder') == 'Chaos Orb Equivalent')
				{
					if (element_input_list[n].value.includes('haos'))
						filter_price_is_chaos = true;
				}
			}
		}
	}
	console.log('filter_price_is_chaos: ' + filter_price_is_chaos.toString() + ', min: ' + filter_price_min_amount.toString() + ', max: ' + filter_price_max_amount.toString());

	
	
	
	
	
	
	
	while (true)
	{
		await sleep(100);
		
		changeTitle();
		
		if (!document.getElementsByTagName('html')[0].outerHTML.includes('Live Search: Searching...'))
			continue;
		
		var element_results_list = document.getElementsByClassName('results');
		if (element_results_list.length <= 0)
			continue;
		
		//console.log('element_results_list.length: ' + element_results_list.length.toString());
		
		var element_resultset_list = element_results_list[0].getElementsByClassName('resultset');
		if (element_resultset_list.length <= 0)
			continue;
		
		//console.log('element_resultset_list.length: ' + element_resultset_list.length.toString());
		
		for (var n = 0; n < element_resultset_list.length; n++)
		{
			var element_dataid_list = element_resultset_list[n].getElementsByTagName('div');
			if (element_dataid_list.length <= 0)
				continue;
			
			for (var i = 0; i < element_dataid_list.length; i++)
			{
				if (element_dataid_list[i].outerHTML.includes('data-id'))
				{
					var start = element_dataid_list[i].outerHTML.indexOf('data-id="') + 9;
					var end = element_dataid_list[i].outerHTML.indexOf('"', start);
					var dataid = element_dataid_list[i].outerHTML.substring(start, end);
					
					if (!data_id_list.includes(dataid))
					{
						data_id_list.push(dataid);
						
						var element_price_list = element_dataid_list[i].getElementsByClassName('price');
						if (element_price_list.length <= 0)
							continue;
						
						var element_span_field_list = element_price_list[0].getElementsByTagName('span')
						if (element_span_field_list.length <= 0)
							continue;
						
						var element_span_data_list = element_span_field_list[0].getElementsByTagName('span')
						if (element_span_data_list.length < 2)
							continue;

						price_amount = element_span_data_list[1].innerHTML;
						
						
						var element_currency_list = element_price_list[0].getElementsByClassName('currency-text currency-image');
						if (element_currency_list.length <= 0)
							continue;
						
						element_span_data_list = element_currency_list[0].getElementsByTagName('span')
						if (element_span_data_list.length <= 0)
							continue;
						
						price_type = element_span_data_list[0].innerHTML;


						var element_whisper_list = element_dataid_list[i].getElementsByClassName('btn btn-default whisper-btn');
						if (element_whisper_list.length <= 0)
							continue;
						
						if (filter_price_is_chaos && price_type.includes('haos'))
						{
							if (price_amount >= filter_price_min_amount && price_amount <= filter_price_max_amount)
							{
								element_whisper_list[0].click();
								element_whisper_list[0].innerHTML = 'Sucked!';
							}
							else
							{
								element_whisper_list[0].innerHTML = 'LOL Wrong!';
							}
						}
						else
						{
							element_whisper_list[0].click();
							element_whisper_list[0].innerHTML = 'Sucked!';
						}
						
						//console.log('price_type: ' + price_type.toString() + ', price_amount: ' + price_amount.toString());
						
						console.log('new item: ' + dataid);
					}
				}
			}
		}
	}
}

setTimeout(main, 0);