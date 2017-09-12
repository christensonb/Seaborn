/*
    This file will contains the behaviors and will automatically be attached
    by the root_namespace mono-behavior
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
using demo.BenChristenson;

namespace demo.BenChristenson.behaviors
{
	
	public class UserLoginEmailPost: ApiBehavior<UserLoginEmailPost>
	{
		public operations.UserLoginEmailPost operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserLoginEmailPost, HttpResponse>  Callback;

	    public string email;                    // str of the email as an alternative to username
        public string password;                 // str of the password

		public models.User responseData;        // User dict

		private void OnSuccess(operations.UserLoginEmailPost operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserLoginEmailPost operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserLoginEmailPost operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserLoginEmailPost, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(string email, string password, Action<operations.UserLoginEmailPost, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			this.email = email;
            this.password = password;

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public models.User Run(string email, string password)
		{ // this will block until complete
			count += 1;
			this.email = email;
            this.password = password;
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserLoginEmailPost().SetParameters(email, password).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class UserLogoutPost: ApiBehavior<UserLogoutPost>
	{
		public operations.UserLogoutPost operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserLogoutPost, HttpResponse>  Callback;

	    

		public string responseData;             // str of a message saying success

		private void OnSuccess(operations.UserLogoutPost operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserLogoutPost operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserLogoutPost operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserLogoutPost, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(Action<operations.UserLogoutPost, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public string Run()
		{ // this will block until complete
			count += 1;
			
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserLogoutPost().SetParameters().Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class UserSignupPut: ApiBehavior<UserSignupPut>
	{
		public operations.UserSignupPut operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserSignupPut, HttpResponse>  Callback;

	    public string username;                 // str of the username give my the player
        public string password;                 // str of the password which will be hashed
        public string email;                    // str of the user's email address
        public string full_name;                // str of the full name

		public models.User responseData;        // User dict of the user created

		private void OnSuccess(operations.UserSignupPut operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserSignupPut operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserSignupPut operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserSignupPut, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(string username, string password, string email, string full_name, Action<operations.UserSignupPut, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			this.username = username;
            this.password = password;
            this.email = email;
            this.full_name = full_name;

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public models.User Run(string username, string password, string email, string full_name)
		{ // this will block until complete
			count += 1;
			this.username = username;
            this.password = password;
            this.email = email;
            this.full_name = full_name;
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserSignupPut().SetParameters(username, password, email, full_name).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class UserLoginPost: ApiBehavior<UserLoginPost>
	{
		public operations.UserLoginPost operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserLoginPost, HttpResponse>  Callback;

	    public string username;                 // str of the username
        public string password;                 // str of the password
        public string email;                    // str of the email as an alternative to username

		public models.User responseData;        // User dict

		private void OnSuccess(operations.UserLoginPost operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserLoginPost operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserLoginPost operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserLoginPost, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(string username, string password, string email, Action<operations.UserLoginPost, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			this.username = username;
            this.password = password;
            this.email = email;

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public models.User Run(string username, string password, string email)
		{ // this will block until complete
			count += 1;
			this.username = username;
            this.password = password;
            this.email = email;
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserLoginPost().SetParameters(username, password, email).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class UserGet: ApiBehavior<UserGet>
	{
		public operations.UserGet operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserGet, HttpResponse>  Callback;

	    

		public models.User responseData;        // User dict of the current user

		private void OnSuccess(operations.UserGet operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserGet operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserGet operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserGet, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(Action<operations.UserGet, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public models.User Run()
		{ // this will block until complete
			count += 1;
			
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserGet().SetParameters().Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class UserPost: ApiBehavior<UserPost>
	{
		public operations.UserPost operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.UserPost, HttpResponse>  Callback;

	    public string username;                 // str of the username give my the player
        public string email;                    // str of the user's email address
        public string full_name;                // str of the full name
        public string password;                 // str of the password which will be hashed

		public models.User responseData;        // User dict of the user updated

		private void OnSuccess(operations.UserPost operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.UserPost operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.UserPost operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.UserPost, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(string username, string email, string full_name, string password, Action<operations.UserPost, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			this.username = username;
            this.email = email;
            this.full_name = full_name;
            this.password = password;

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public models.User Run(string username, string email, string full_name, string password)
		{ // this will block until complete
			count += 1;
			this.username = username;
            this.email = email;
            this.full_name = full_name;
            this.password = password;
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.UserPost().SetParameters(username, email, full_name, password).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
}
