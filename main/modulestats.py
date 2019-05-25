from .moduledata import _MODULE_DATA

column_names = {
    'FR': {
        'AOEDamage_BS': 'Dégâts de zone (EB)',
        'AOEDamage_WS': 'Dégâts de zone (WS)',
        'APTPIOTTP': 'Délai/cargaison',
        'ActivationDelay': 'Cooldown',
        'ActivationFuelCost': 'Activation',
        'ActivationHydroOnBoard': 'Coût (H miné)',
        'ActivationPrep': 'Délai',
        'ActivationPrepBS': 'Délai (EB)',
        'ActivationPrepWS': 'Délai (WS)',
        'ActivationType': 'Type d\'activation',
        'AdditionalDPSPerTargetInRange': '+DPS/ennemi',
        'AllowedStarTypes': 'Étoiles autorisées',
        'ApplyAOEDamageOnDestroy': 'Dégâts de zone à la destruction',
        'AutoActivateHealth': 'HP pour activation',
        'AwardLevel': 'Niveau de RS',
        'BCCost': 'Install.',
        'BSOnly': 'Seulement pour cuirassés',
        'BSScore': 'Score EB',
        'DPS': 'DPS',
        'DamageReductionPct': 'Réduction de dégâts',
        'DeactivateOnJump': 'Saut impossible',
        'DisableActivationDuringPrep': 'Désactivé pendant les délais d\'activation',
        'DoNotAward': 'Pas obtenable',
        'DroneShipmentBonus': 'Bonus par cargaison',
        'EffectDurationx10': 'Durée',
        'EffectDurationx10BS': 'Durée (EB)',
        'EffectDurationx10WS': 'Durée (WS)',
        'EffectRadius': 'Rayon',
        'EffectRadiusBS': 'Rayon (EB)',
        'EffectRadiusWS': 'Rayon (WS)',
        'ExtraHydrogenStorage': 'Stockage d\'hydro supplémentaire [inutilisé]',
        'ExtraMineralStorage': 'Capacité',
        'ExtraTradeSlots': 'Capacité',
        'FuelUseIncrease': 'Consommation',
        'Hide': 'Caché',
        'HideSelection': 'Caché',
        'HydroPerNewAsteroid': 'Hydro par astéroide créé',
        'HydroUploadPct': 'Transfert H',
        'IncreaseSectorHydroPct': 'Augmentation H',
        'InitialBlueprints': 'Plans initiaux',
        'InstantHydrogenCollected': 'Hydro collecté',
        'IsAOEOnlyShield': 'Bouclier AOE seulement',
        'IsAreaShield': 'Bouclier de zone',
        'IsBarrier': 'Barrière',
        'IsEMP': 'IEM',
        'IsStealth': 'Discrétion',
        'IsSupress': 'Supression',
        'IsTaunt': 'Fortification',
        'IsTeleport': 'Téléport',
        'JobPayoutIncreasePercent': 'Bonus cargaisons',
        'JumpToSafety': 'Sanctuaire',
        'Level': 'Niv',
        'MaxDPS': 'DPS maxi',
        'MaxDPSTime': 'Temps de chargement',
        'MaxDPSTime_BS': 'Temps de chargement (EB)',
        'MaxImpulse': 'Impulsion max',
        'MaxNewAsteroids': 'Max de nouveaux astéroides',
        'MaxTargets': 'Max de cibles',
        'MinPublicRSLevel': 'Niveau de RS publique min',
        'MineAllInSector': 'Forage multiple',
        'MiningSpeedModifierPct': 'Multiplicateur de vitesse de forage',
        'MirrorDamagePct': 'Dégâts réfléchis',
        'PreventShieldDuringActivation': 'Interdit les boucliers pendant l\'activation',
        'PreventUseOnWsJumpgate': 'Désactivé sur la porte de saut (WS)',
        'PullShips': 'Lien',
        'RedStarLifeExtention': 'Extension d\'étoile rouge',
        'RepairHullPointsPerSecond': 'Réparation',
        'ReqEnemyShipsInSector': 'Requiert des ennemis dans le secteur',
        'SalvageHullPercent': 'PV/ennemi',
        'ShieldRegenDelay': 'Délai de régénération',
        'ShieldStrength': 'Bouclier',
        'ShowBSInfo': 'Affichage des valeurs EB',
        'ShowWSInfo': 'Affichage des valeurs WS',
        'SlotType': 'Type de module',
        'SpawnCapacity': 'Capacité',
        'SpawnLifetime': 'Durée de vie',
        'SpawnLifetime_WS': 'Durée de vie (WS)',
        'SpawnedShip': 'Vaisseau créé',
        'SpeedIncrDuringActivation': 'Bonus de vitesse',
        'SpeedIncreasePerShipment': 'Bonus de vitesse par cargaison',
        'StopCountdownOnDisable': 'Pause du délai d\'activation si désactivé',
        'SwapLoadWithOtherTransport': 'Tranfert de la cargaison',
        'TeleportShipments': 'Téléport vers le maximum de cargaisons',
        'TeleportToClosestCombat': 'Téléport vers le combat le plus proche',
        'TeleportToRandomSector': 'Téléport aléatoire',
        'TeleportToTradeStation': 'Téléport vers station d\'échange',
        'TimeToFullyRegen': 'Temps de régénération complète',
        'TimeWarpFactor': 'Distortion temporelle',
        'TradeBurstShipmentBonus': 'Bonus',
        'TradeBurstShipmentsStart': 'Livraisons avant bonus',
        'TradeStationDeliverReward': 'Multiplicateur au déchargement',
        'UnityBoostPercent': 'Boost par allié',
        'UnlockBlueprints': 'Plans',
        'UnlockPrice': 'Déblocage',
        'UnlockTime': 'Déblocage',
        'WaypointShipmentRewardBonus': 'Bonus',
        'WhiteStarScore': 'Score WS',
    }
}

column_order = (
    'Level',
    'UnlockPrice', 'UnlockBlueprints', 'UnlockTime', 'BCCost',
    'ActivationType' 'ActivationHydroOnBoard', 'ActivationDelay', 'ActivationPrep', 'ActivationPrepWS', 'ActivationPrepBS'
    'EffectDurationx10', 'EffectDurationx10WS', 'EffectDurationx10BS', 'EffectRadius', 'EffectRadiusWS', 'EffectRadiusBS',
    'DPS', 'MaxDPS', 'MaxDPSTime', 'MaxDPSTime_BS',
    'FuelUseIncrease', 'ActivationFuelCost',
    'WhiteStarScore', 'BSScore',
)

ignore_values = (
    'PullShips', 'MineAllInSector', 'IsAOEOnlyShield', 'IsAreaShield',
    'IsBarrier', 'IsEMP', 'IsSupress', 'IsStealth', 'IsTeleport', 'IsTaunt',
    'JumpToSafety', 'Hide', 'HideSelection', 'DoNotAward',
    'ShowBSInfo', 'ShowWSInfo', 'SwapLoadWithOtherTransport',
    'TeleportShipments', 'TeleportToClosestCombat', 'TeleportToRandomSector', 'TeleportToTradeStation',
)

time_values = (
    'ActivationDelay', 'ActivationPrep', 'ActivationPrepWS', 'ActivationPrepBS',
    'EffectDurationx10', 'EffectDurationx10WS', 'EffectDurationx10BS',
    'MaxDPSTime', 'MaxDPSTime_BS', 'ShieldRegenDelay',
    'RedStarLifeExtention', 'SpawnLifetime', 'SpawnLifetime_WS',
    'UnlockTime', 'TimeToFullyRegen',
)

bool_values = (
    'StopCountdownOnDisable', 'ReqEnemyShipsInSector', 'PreventUseOnWsJumpgate',
    'DisableActivationDuringPrep', 'DeactivateOnJump', 'BSOnly', 'PreventShieldDuringActivation'
)

credits_values = (
    'UnlockPrice', 'BCCost',
)

hydro_values = (
    'ActivationFuelCost', 'ActivationHydroOnBoard',
    'ExtraHydrogenStorage', 'ExtraMineralStorage',
    'FuelUseIncrease', 'HydroPerNewAsteroid', 'InstantHydrogenCollected',
)

percent_values = (
    'DamageReductionPct', 'DroneShipmentBonus',
    'HydroUploadPct', 'IncreaseSectorHydroPct', 'JobPayoutIncreasePercent',
    'MirrorDamagePct', 'SalvageHullPercent', 'SpeedIncrDuringActivation', 'SpeedIncreasePerShipment',
    'TradeBurstShipmentBonus', 'UnityBoostPercent', 'WaypointShipmentRewardBonus',
)

values_translations = {
    'FR': {
        'Passive': 'Passif',
        'Activated': 'Activable',
        'Trade': 'Commerce',
        'Mining': 'Forage',
        'Weapon': 'Arme',
        'Shield': 'Bouclier',
        'Support': 'Support',

        '_yes': 'Oui',
        '_no': 'Non',
        '_day': 'j',
        '_hour': 'h',
        '_minute': 'm',
        '_second': 's',
    }
}
