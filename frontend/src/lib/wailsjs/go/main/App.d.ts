// Cynhyrchwyd y ffeil hon yn awtomatig. PEIDIWCH Â MODIWL
// This file is automatically generated. DO NOT EDIT
import {games} from '../models';
import {afkjourney} from '../models';
import {config} from '../models';

export function GetEditableGameConfig(arg1:games.Game):Promise<{[key: string]: any}>;

export function GetEditableMainConfig():Promise<{[key: string]: any}>;

export function GetRunningSupportedGame():Promise<games.Game>;

export function IsGameProcessRunning():Promise<boolean>;

export function SaveAFKJourneyConfig(arg1:games.Game,arg2:afkjourney.Config):Promise<void>;

export function SaveMainConfig(arg1:config.MainConfig):Promise<void>;

export function StartGameProcess(arg1:games.Game,arg2:Array<string>):Promise<void>;

export function TerminateGameProcess():Promise<void>;

export function UpdatePatch(arg1:string):Promise<void>;
