/*
    This file will initialize the REST engine
    It should be attached to the REST game object
*/

using UnityEngine;
using System;
using System.Collections;
using hg.ApiWebKit.core.http;
using hg.ApiWebKit.apis;
using hg.ApiWebKit;
using demo.BenChristenson;

public class BenChristensonApiInitialize : ApiWebKitInitialize
{
    public enum BaseUriEnum { remote, remoteSSL, local, debug, debugSSL, proxyRemote, proxyDebug, proxyRemoteSSL };
    public BaseUriEnum base_uri = BaseUriEnum.remote;

    public enum BehaviorCreationEnum { StartupKeep, JustInTimeKeep, JustInTimeDestroy }
    public BehaviorCreationEnum behaviorsCreation = BehaviorCreationEnum.JustInTimeKeep;

    public float timeout = 9f;

	public bool LogVerbose = false;
	public bool LogInfo = true;
	public bool LogWarning = true;
	public bool LogError = true;

	public override void Awake()
	{
		Configuration.SetSetting ("log-VERBOSE", LogVerbose);
		Configuration.SetSetting ("log-INFO", LogInfo);
		Configuration.SetSetting ("log-WARNING", LogWarning);
		Configuration.SetSetting ("log-ERROR", LogError);
		Configuration.SetSetting("default-http-client", typeof(hg.ApiWebKit.providers.HttpWWWClient));
		Configuration.SetSetting("request-timeout", timeout);
        Configuration.SetSetting("persistent-game-object-name", "BenChristensonApi");


         switch (base_uri)
         {
            case BaseUriEnum.remoteSSL:
                Configuration.SetBaseUri("PuzzlesAndPotions", "https://api.PuzzlesAndPotions.com");
                break;
            case BaseUriEnum.remote:
                 Configuration.SetBaseUri("PuzzlesAndPotions", "http://api.PuzzlesAndPotions.com");
                 break;
            case BaseUriEnum.debug:
                Configuration.SetBaseUri("PuzzlesAndPotions", "http://127.0.0.1:4999");
                break;
            case BaseUriEnum.debugSSL:
                Configuration.SetBaseUri("PuzzlesAndPotions", "https://127.0.0.1:4999");
                break;
            case BaseUriEnum.proxyRemote:
                Configuration.SetBaseUri("PuzzlesAndPotions", "http://127.0.0.1:4888");
                break;
            case BaseUriEnum.proxyDebug:
                Configuration.SetBaseUri("PuzzlesAndPotions", "http://127.0.0.1:4777");
                break;
            case BaseUriEnum.proxyRemoteSSL:
                Configuration.SetBaseUri("PuzzlesAndPotions", "https://127.0.0.1:4666");
                break;
        }
	}

    public bool is_behaviors_created_at_startup()
    {
        return behaviorsCreation == BehaviorCreationEnum.StartupKeep;
    }

    public bool is_just_in_time_create()
    {
        return behaviorsCreation != BehaviorCreationEnum.JustInTimeKeep;
    }

    public bool is_behavior_destroyed_on_complete()
    {
        return behaviorsCreation == BehaviorCreationEnum.JustInTimeDestroy;
    }

	// Update is called once per frame
	void Update () {

	}
}

