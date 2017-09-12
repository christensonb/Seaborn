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

namespace %(namespace)s
{
	public class  %(short_namespace)s : MonoBehaviour
	{
	    %(behaviors_declarations)s

		public virtual void Awake()
		{
            %(short_namespace)sApiInitialize %(short_namespace_instant)sApiInitialize = GetComponent<%(short_namespace)sApiInitialize>();
            if (%(short_namespace_instant)sApiInitialize.is_behaviors_created_at_startup())
            {
			    %(behaviors_instantiation)s
			}
		}
	}
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

namespace api.MechanicsOfPlay
{
	public class  MechanicsOfPlay : MonoBehaviour
	{
		public behaviors.HelloEchoGet helloEchoGet;
		public behaviors.HelloWaitGet helloWaitGet;

		public virtual void Start()
		{
			helloEchoGet = gameObject.AddComponent<behaviors.HelloEchoGet> ();
			helloWaitGet = gameObject.AddComponent<behaviors.HelloWaitGet> ();
		}
	}

		public sealed class MechanicsOfPlayApiMonitor: ApiMonitor
	{
	}
}
*/


