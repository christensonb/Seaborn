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
using %(namespace)s;

namespace %(namespace)s.behaviors
{
	/* Endpoint Code Here */
	public class %(name)s: ApiBehavior<%(name)s>
	{
		public operations.%(name)s operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.%(name)s, HttpResponse>  Callback;

	    %(arg_declarations)s

		public %(response_type)s responseData; %(response_desc)s

		private void OnSuccess(operations.%(name)s operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.%(name)s operation, HttpResponse response)
		{
			responseData = %(null)s;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.%(name)s operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.%(name)s, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, %(short_namespace)sApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(%(args_with_comma)sAction<operations.%(name)s, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			%(arg_assignments)s

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public %(response_type)s Run(%(args)s)
		{ // this will block until complete
			count += 1;
			%(arg_assignments)s
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.%(name)s().SetParameters(%(arg_params)s).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
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

namespace api.MechanicsOfPlay.behaviors
{

	public class HelloEchoGet: ApiBehavior<HelloEchoGet>
	{
		public string message;

	    private Action<operations.HelloEchoGet, HttpResponse>  OnComplete;

		ApiBehaviorStatus Status;
		string responseData;

		private void OnSuccess(operations.HelloEchoGet operations, HttpResponse response)
		{
            responseData = operations.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.HelloEchoGet operations, HttpResponse response)
		{
            responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		public void Spawn(string message,  Action<operations.HelloEchoGet, HttpResponse> OnComplete)
		{ // this will spawn a thread to handle the rest call and return immediately
			this.OnComplete = OnComplete;
			this.message = message;
			StartCoroutine(this.ExecuteAndWait());
		}

		public string Run(string message)
		{ // this will block until complete
			this.message = message;
			ExecutableCode();
			if (Status == ApiBehaviorStatus.SUCCESS)
				return responseData;
			return "";
		}

		public override void ExecutableCode()
		{
			new operations.HelloEchoGet()
				.SetParameters(message)
					.Send(OnSuccess, OnFail, OnComplete);
		}
	}


	public class HelloWaitGet: ApiBehavior<HelloWaitGet>
	{
		public int seconds;

		ApiBehaviorStatus Status;
		string ResponseData;
	    private Action<operations.HelloWaitGet, HttpResponse>  OnComplete;

		private void OnSuccess(operations.HelloWaitGet operations, HttpResponse response)
		{
			ResponseData = operations.Response;
			Status = ApiBehaviorStatus.SUCCESS;
			OnCompletion(operations, response, MechanicsOfPlayApiMonitor.Instance);
		}

		private void OnFail(operations.HelloWaitGet operations, HttpResponse response)
		{
			ResponseData = null;
			Status = ApiBehaviorStatus.FAILURE;
			OnCompletion(operations, response, MechanicsOfPlayApiMonitor.Instance);
		}

		public void Spawn(int seconds,  Action<operations.HelloWaitGet, HttpResponse> OnComplete)
		{ // this will spawn a thread to handle the rest call and return immediately
			this.OnComplete = OnComplete;
			this.seconds = seconds;
			StartCoroutine(this.ExecuteAndWait());
		}

		public string Run(int seconds)
		{ // this will block until complete

			this.seconds = seconds;
			ExecutableCode();
			if (Status == ApiBehaviorStatus.SUCCESS)
				return ResponseData;
			return null;
		}

		public override void ExecutableCode()
		{
			new operations.HelloWaitGet ()
				.SetParameters (seconds)
					.Send (OnSuccess, OnFail, null); // OnComplete);
		}
	}
}
*/




