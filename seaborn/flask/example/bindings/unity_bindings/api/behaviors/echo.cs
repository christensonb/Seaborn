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
	
	public class EchoMessageGet: ApiBehavior<EchoMessageGet>
	{
		public operations.EchoMessageGet operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.EchoMessageGet, HttpResponse>  Callback;

	    public string message = "hello";        // str of the message to echo

		public string responseData;             // str of the message echoed

		private void OnSuccess(operations.EchoMessageGet operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.EchoMessageGet operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.EchoMessageGet operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.EchoMessageGet, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(string message, Action<operations.EchoMessageGet, HttpResponse> Callback)
		{ // this will spawn a thread to handle the rest call and return immediately
			count += 1;
			this.Callback = Callback;
			this.message = message;

 			StartCoroutine(this.ExecuteAndWait());

			/*
			if (hg.ApiWebKit.Configuration.GetSetting<bool?>("Wait_Before_Returning") == true){
                while(!this._completed){
			        new WaitForSeconds(1);
			    }
			}*/
		}

		public string Run(string message)
		{ // this will block until complete
			count += 1;
			this.message = message;
			ExecutableCode();
			return responseData;
		}

		public override void ExecutableCode()
		{
			new operations.EchoMessageGet().SetParameters(message).Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
	public class EchoGet: ApiBehavior<EchoGet>
	{
		public operations.EchoGet operation;
		private int count;   			// count of the number of concurrent calls happening right now
		public bool DestroyOnComplete = false;
	    private Action<operations.EchoGet, HttpResponse>  Callback;

	    

		public string responseData;             // str of "Hello World!"

		private void OnSuccess(operations.EchoGet operation, HttpResponse response)
		{
			responseData = operation.responseData;
			Status = ApiBehaviorStatus.SUCCESS;
		}

		private void OnFail(operations.EchoGet operation, HttpResponse response)
		{
			responseData = null;
			Status = ApiBehaviorStatus.FAILURE;
		}

		private void OnComplete(operations.EchoGet operation, HttpResponse response)
		{
			this.operation = operation;
			Action<operations.EchoGet, HttpResponse> LocalCallback = Callback;
			OnCompletion(operation, response, BenChristensonApiMonitor.Instance);    // this will free up the behavior to accept another call
			count -= 1;
			LocalCallback(operation, response);   // this is the project's custom OnComplete
			if (DestroyOnComplete){
				this.Destroy();
			}
		}

		public void Spawn(Action<operations.EchoGet, HttpResponse> Callback)
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
			new operations.EchoGet().SetParameters().Send(OnSuccess, OnFail, OnComplete);
		}

        public void Destroy()
        {
            if (count == 0) {
                Destroy(this);
            }
        }
	}

	
}
