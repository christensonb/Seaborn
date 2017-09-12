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
	
	[HttpPOST]
	[HttpPath("BenChristenson","user/login/email")]
	public class UserLoginEmailPost: HttpOperation
	{
	    [HttpFormField] public string email;                    // str of the email as an alternative to username
        [HttpFormField] public string password;                 // str of the password

		[HttpResponseJsonBody]
		public models.User responseData;        // User dict

		public UserLoginEmailPost SetParameters(string email, string password)
		{
		    this.email = email;
            this.password = password;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

	
	[HttpPOST]
	[HttpPath("BenChristenson","user/logout")]
	public class UserLogoutPost: HttpOperation
	{
	    

		[HttpResponseJsonBody]
		public string responseData;             // str of a message saying success

		public UserLogoutPost SetParameters()
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

	
	[HttpPOST]
	[HttpPath("BenChristenson","user/signup/put")]
	public class UserSignupPut: HttpOperation
	{
	    [HttpFormField] public string username;                 // str of the username give my the player
        [HttpFormField] public string password;                 // str of the password which will be hashed
        [HttpFormField] public string email;                    // str of the user's email address
        [HttpFormField] public string full_name;                // str of the full name

		[HttpResponseJsonBody]
		public models.User responseData;        // User dict of the user created

		public UserSignupPut SetParameters(string username, string password, string email, string full_name)
		{
		    this.username = username;
            this.password = password;
            this.email = email;
            this.full_name = full_name;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

	
	[HttpPOST]
	[HttpPath("BenChristenson","user/login")]
	public class UserLoginPost: HttpOperation
	{
	    [HttpFormField] public string username;                 // str of the username
        [HttpFormField] public string password;                 // str of the password
        [HttpFormField] public string email;                    // str of the email as an alternative to username

		[HttpResponseJsonBody]
		public models.User responseData;        // User dict

		public UserLoginPost SetParameters(string username, string password, string email)
		{
		    this.username = username;
            this.password = password;
            this.email = email;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

	
	[HttpGET]
	[HttpPath("BenChristenson","user")]
	public class UserGet: HttpOperation
	{
	    

		[HttpResponseJsonBody]
		public models.User responseData;        // User dict of the current user

		public UserGet SetParameters()
		{
		    
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

	
	[HttpPOST]
	[HttpPath("BenChristenson","user")]
	public class UserPost: HttpOperation
	{
	    [HttpFormField] public string username;                 // str of the username give my the player
        [HttpFormField] public string email;                    // str of the user's email address
        [HttpFormField] public string full_name;                // str of the full name
        [HttpFormField] public string password;                 // str of the password which will be hashed

		[HttpResponseJsonBody]
		public models.User responseData;        // User dict of the user updated

		public UserPost SetParameters(string username, string email, string full_name, string password)
		{
		    this.username = username;
            this.email = email;
            this.full_name = full_name;
            this.password = password;
			return this;
		}

		protected override void FromResponse(HttpResponse response)
		{
			base.FromResponse(response);
		}
	}

	
}
