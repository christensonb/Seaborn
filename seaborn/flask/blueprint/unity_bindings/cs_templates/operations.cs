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

namespace %(namespace)s.operations
{
	/* Endpoint Code Here */
	[Http%(method)s]
	[HttpPath("%(short_namespace)s","%(sub_uri)s")]
	public class %(name)s: HttpOperation
	{
	    %(arg_queries)s

		[HttpResponseJsonBody]
		public %(response_type)s responseData; %(response_desc)s

		public %(name)s SetParameters(%(args)s)
		{
		    %(arg_assignments)s
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			%(response_converter)s
		}
	}

	/* Endpoint Code Here */
}
/*$$   --------- Examples ---------
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

namespace api.MechanicsOfPlay.operations
{
	[HttpGET]
	[HttpPath("MechanicsOfPlay","/hello/echo")]
    [HttpContentType("application/json")]
	public class HelloEchoGet: HttpOperation
	{
		[HttpQueryString]
		public string message = "default";

		[HttpResponseJsonBody]
		public string responseData;

		public HelloEchoGet SetParameters(string message)
		{
			this.message = message;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
            responseData = response.Text;
		}
	}

	[HttpGET]
	[HttpPath("MechanicsOfPlay","/hello/wait")]
    [HttpContentType("application/json")]
    public class HelloWaitGet: HttpOperation
	{
		[HttpQueryString]
		public int seconds=4;

		[HttpResponseJsonBody]
		public string responseData;

		public HelloWaitGet SetParameters(int seconds)
		{
			this.seconds = seconds;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

    [HttpGET]
    [HttpPath("MechanicsOfPlay", "/hello/key")]
    [HttpContentType("application/json")]
    public class HelloKeyGet : HttpOperation
    {
        [HttpQueryString]
        public string key="hello";

        [HttpResponseJsonBody]
        public models.Hello responseData;

        public HelloKeyGet SetParameters(string key)
        {
            this.key = key;
            return this;
        }

        protected override void FromResponse(HttpResponse response)
        {
            base.FromResponse(response);
        }
    }

    [HttpPOST]
    [HttpPath("MechanicsOfPlay", "/hello/key/put")]
    [HttpContentType("application/json")]
    public class HelloKeyPut : HttpOperation
    {
        [HttpQueryString]
        public string key = "hello";

        [HttpQueryString]
        public string value;


        [HttpResponseJsonBody]
        public models.Hello responseData;

        public HelloKeyPut SetParameters(string key, string value)
        {
            this.key = key;
            this.value = value;
            return this;
        }

        protected override void FromResponse(HttpResponse response)
        {
            base.FromResponse(response);
        }
    }
}


*/