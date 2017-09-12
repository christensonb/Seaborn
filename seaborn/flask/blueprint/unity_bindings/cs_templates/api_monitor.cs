/*
    This file will monitor and give statistics on the REST calls
    It may be attached to the REST game object
*/

using UnityEngine;
using System;
using System.Collections;
using hg.ApiWebKit.core.http;
using hg.ApiWebKit.apis;

namespace %(namespace)s
{
	public sealed class %(short_namespace)sApiMonitor: ApiMonitor
	{

	}
}

/*$$   --------- Examples ---------
using UnityEngine;
using System;
using System.Collections;
using hg.ApiWebKit.core.http;

namespace api.MechanicsOfPlay
{
	public sealed class MechanicsOfPlayApiMonitor: ApiMonitor
	{

	}
}