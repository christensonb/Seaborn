/*
    This file contains the operations code for the REST Endpoint
    It is the lowest level code before the WAK library.
*/

using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using hg.ApiWebKit;
using hg.ApiWebKit.core.http;
using hg.ApiWebKit.faulters;
using hg.ApiWebKit.mappers;
using hg.ApiWebKit.core.attributes;
using hg.ApiWebKit.apis;

namespace demo.BenChristenson.operations
{
	
	[HttpGET]
	[HttpPath("BenChristenson","echo/message")]
	public class EchoMessageGet: HttpOperation
	{
	    [HttpQueryString] public string message = "hello";        // str of the message to echo

		[HttpResponseJsonBody]
		public string responseData;             // str of the message echoed

		public EchoMessageGet SetParameters(string message)
		{
		    this.message = message;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			if(response.HasError)
                return;
            else
                this.responseData = response.Text.Substring(1,response.Text.Length-2);
		}
	}

	
	[HttpGET]
	[HttpPath("BenChristenson","echo")]
	public class EchoGet: HttpOperation
	{
	    

		[HttpResponseJsonBody]
		public string responseData;             // str of "Hello World!"

		public EchoGet SetParameters()
		{
		    
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			if(response.HasError)
                return;
            else
                this.responseData = response.Text.Substring(1,response.Text.Length-2);
		}
	}

	
}
