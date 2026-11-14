#pragma once
// WeirdExt offsets — macOS ARM64
//
// Roblox Version  : 0.745.0.7451137
// Binary SHA-256  : 8af3f95d347a5283618dd9c17f4a1b02b59982ff699f00cc6f2a195377f2f6b7
// Dumped At       : 2026-11-14 21:02 UTC
// Total Offsets   : 2318 (29 confirmed live, 2289 from reflection)
//
// macOS layouts differ from Windows; use these with the macOS client only.

#include <cstdint>

namespace Offsets {
    namespace Instance {
        inline constexpr uintptr_t Name = 0x68;  // pointer to std::string
        inline constexpr uintptr_t Parent = 0x60;
        inline constexpr uintptr_t ChildrenStart = 0x70;  // pointer to a vector of 16-byte smart pointers
        inline constexpr uintptr_t ChildrenEnd = 0x8;  // end pointer, relative to the children vector
        inline constexpr uintptr_t This = 0x8;  // (self, control block) smart pointer pair
        inline constexpr uintptr_t numExpectedDirectChildren = 0x80;  // int
    }
    namespace Players {
        inline constexpr uintptr_t LocalPlayer = 0x108;
        inline constexpr uintptr_t BanningEnabled = 0x124;  // bool
        inline constexpr uintptr_t CharacterAutoLoads = 0x125;  // bool
        inline constexpr uintptr_t MaxPlayersInternal = 0x118;  // int
        inline constexpr uintptr_t PreferredPlayersInternal = 0x11c;  // int
        inline constexpr uintptr_t RespawnTime = 0x120;  // float
        inline constexpr uintptr_t ServerGitHash = 0xa8;
        inline constexpr uintptr_t ServerLogPrefix = 0xc0;
        inline constexpr uintptr_t UseStrafingAnimations = 0x126;  // bool
    }
    namespace Player {
        inline constexpr uintptr_t ModelInstance = 0x258;
        inline constexpr uintptr_t Team = 0x298;
        inline constexpr uintptr_t AccountAgeReplicate = 0x31c;  // int
        inline constexpr uintptr_t AgeChecked = 0x320;  // Enums::AgeCheckStatus
        inline constexpr uintptr_t AutoJumpEnabled = 0x381;  // bool
        inline constexpr uintptr_t CameraFieldOfView = 0x324;  // float
        inline constexpr uintptr_t CameraFrustumRequested = 0x382;  // bool
        inline constexpr uintptr_t CameraMaxZoomDistance = 0x328;  // float
        inline constexpr uintptr_t CameraMinZoomDistance = 0x32c;  // float
        inline constexpr uintptr_t CameraMode = 0x330;  // Enums::CameraModeEnum::CameraMode
        inline constexpr uintptr_t CameraViewportSize = 0x314;  // Vector2
        inline constexpr uintptr_t CanLoadCharacterAppearance = 0x383;  // bool
        inline constexpr uintptr_t CharacterAppearance = 0xc0;
        inline constexpr uintptr_t CharacterAppearanceId = 0x2c0;  // int64
        inline constexpr uintptr_t ChararacterRegionId = 0x308;  // Vector3
        inline constexpr uintptr_t ChatAvailabilityStatus = 0xd8;
        inline constexpr uintptr_t ChatPrivacyMode = 0x334;  // Enums::ChatPrivacyModeEnum::ChatPrivacyMode
        inline constexpr uintptr_t CloudEditCameraCoordinateFrame = 0x2d8;  // CoordinateFrame
        inline constexpr uintptr_t CloudEditPlayerActive = 0x384;  // bool
        inline constexpr uintptr_t CountryRegionCodeReplicate = 0xf0;
        inline constexpr uintptr_t DataComplexityLimit = 0x338;  // int
        inline constexpr uintptr_t DevCameraOcclusionMode = 0x33c;  // Enums::DevCameraOcclusionModeEnum::DeveloperCameraOcclusionMode
        inline constexpr uintptr_t DevComputerCameraMode = 0x340;  // Enums::DevComputerCameraMovementModeEnum::DeveloperComputerCameraMovementMode
        inline constexpr uintptr_t DevComputerMovementMode = 0x344;  // Enums::DevComputerMovementModeEnum::DeveloperComputerMovementMode
        inline constexpr uintptr_t DevEnableMouseLock = 0x386;  // bool
        inline constexpr uintptr_t DevTouchCameraMode = 0x348;  // Enums::DevTouchCameraMovementModeEnum::DeveloperTouchCameraMovementMode
        inline constexpr uintptr_t DevTouchMovementMode = 0x34c;  // Enums::DevTouchMovementModeEnum::DeveloperTouchMovementMode
        inline constexpr uintptr_t DisplayName = 0x108;
        inline constexpr uintptr_t FollowUserIdReplicated = 0x2c8;  // int64
        inline constexpr uintptr_t FrustumStreaming = 0x354;  // Enums::FrustumStreamingMode
        inline constexpr uintptr_t GameplayPaused = 0x387;  // bool
        inline constexpr uintptr_t HasRobloxSubscription = 0x388;  // bool
        inline constexpr uintptr_t HasVerifiedBadge = 0x389;  // bool
        inline constexpr uintptr_t HealthDisplayDistance = 0x358;  // float
        inline constexpr uintptr_t InputLatency = 0x35c;  // int
        inline constexpr uintptr_t InternalCharacterAppearanceLoaded = 0x38a;  // bool
        inline constexpr uintptr_t MaximumSimulationRadius = 0x360;  // float
        inline constexpr uintptr_t MembershipTypeReplicate = 0x364;  // MembershipType
        inline constexpr uintptr_t NameDisplayDistance = 0x368;  // float
        inline constexpr uintptr_t NeedRegionalFallback = 0x38b;  // bool
        inline constexpr uintptr_t Neutral = 0x38c;  // bool
        inline constexpr uintptr_t OsPlatform = 0x120;
        inline constexpr uintptr_t PartyId = 0x138;
        inline constexpr uintptr_t PlatformName = 0x150;
        inline constexpr uintptr_t RawJoinData = 0x168;  // BinaryString
        inline constexpr uintptr_t SimulationRadius = 0x36c;  // float
        inline constexpr uintptr_t TeamColor = 0x370;  // BrickColor
        inline constexpr uintptr_t TeleportedIn = 0x38e;  // bool
        inline constexpr uintptr_t UserIdModeReplicate = 0x378;  // UserIdMode
        inline constexpr uintptr_t VRDevice = 0x180;
        inline constexpr uintptr_t VREnabled = 0x390;  // bool
        inline constexpr uintptr_t VoiceChatVolume = 0x37c;  // float
    }
    namespace Workspace {
        inline constexpr uintptr_t CurrentCamera = 0x458;
        inline constexpr uintptr_t AirTurbulenceIntensity = 0x490;  // float
        inline constexpr uintptr_t AllowThirdPartySales = 0x538;  // bool
        inline constexpr uintptr_t AuthorityMode = 0x494;  // Enums::AuthorityMode
        inline constexpr uintptr_t AvatarUnificationMode = 0x498;  // Enums::AvatarUnificationMode
        inline constexpr uintptr_t ClientAnimatorThrottling = 0x49c;  // Enums::ClientAnimatorThrottlingMode
        inline constexpr uintptr_t DistributedGameTime = 0x478;  // double
        inline constexpr uintptr_t EnableSLIMAvatars = 0x4a0;  // Enums::RolloutState
        inline constexpr uintptr_t ExpandedTerrain = 0x4a4;  // Enums::RolloutState
        inline constexpr uintptr_t FallHeightEnabled = 0x53a;  // bool
        inline constexpr uintptr_t FluidForces = 0x4a8;  // Enums::FluidForceModelMode
        inline constexpr uintptr_t IKControlConstraintSupport = 0x4ac;  // Enums::IkControlConstraintSupport
        inline constexpr uintptr_t ImprovedAnimationConstraint = 0x4b0;  // Enums::RolloutState
        inline constexpr uintptr_t ImprovedPhysicsReplication = 0x4b4;  // Enums::RolloutState
        inline constexpr uintptr_t InsertPoint = 0x578;  // Vector3
        inline constexpr uintptr_t InterpolationThrottling = 0x4b8;  // Enums::InterpolationThrottlingMode
        inline constexpr uintptr_t LayeredClothingCacheOptimizations = 0x4bc;  // Enums::RolloutState
        inline constexpr uintptr_t LuauTypeCheckMode = 0x4c0;  // Enums::LuauTypeCheckMode
        inline constexpr uintptr_t MapTVRemoteToGamepadKeycodes = 0x4c4;  // Enums::RolloutState
        inline constexpr uintptr_t MeshPartHeadsAndAccessories = 0x4c8;  // Enums::MeshPartHeadsAndAccessories
        inline constexpr uintptr_t MeshStreamingAndImprovedLods = 0x4cc;  // Enums::RolloutState
        inline constexpr uintptr_t ModelStreamingBehavior = 0x4d0;  // Enums::ModelStreamingBehavior
        inline constexpr uintptr_t PathfindingUseImprovedSearch = 0x4d8;  // Enums::PathfindingUseImprovedSearch
        inline constexpr uintptr_t PhysicsSteppingMethod = 0x4dc;  // Enums::PhysicsSteppingMethod
        inline constexpr uintptr_t PlayerCharacterDestroyBehavior = 0x4e0;  // Enums::PlayerCharacterDestroyBehavior
        inline constexpr uintptr_t PredictiveStreamingMode = 0x4e8;  // Enums::PredictiveStreamingMode
        inline constexpr uintptr_t PrimalPhysicsSolver = 0x4ec;  // Enums::PrimalPhysicsSolverMode
        inline constexpr uintptr_t RejectCharacterDeletions = 0x4f0;  // RejectCharacterDeletions
        inline constexpr uintptr_t RenderingCacheOptimizations = 0x4f4;  // Enums::RenderingCacheOptimizationMode
        inline constexpr uintptr_t ReplicateInstanceDestroySetting = 0x4f8;  // Enums::ReplicateInstanceDestroySetting
        inline constexpr uintptr_t ReplicationFrequency = 0x4fc;  // Enums::ReplicationMode
        inline constexpr uintptr_t ReplicationThroughput = 0x500;  // Enums::ReplicationMode
        inline constexpr uintptr_t Retargeting = 0x504;  // Enums::AnimatorRetargetingMode
        inline constexpr uintptr_t SandboxedInstanceMode = 0x508;  // Enums::SandboxedInstanceMode
        inline constexpr uintptr_t StreamOutBehavior = 0x510;  // Enums::StreamOutBehavior
        inline constexpr uintptr_t StreamingAdaptiveRadius = 0x53b;  // bool
        inline constexpr uintptr_t StreamingEnabledStorage = 0x53c;  // bool
        inline constexpr uintptr_t StreamingIntegrityMode = 0x514;  // Enums::StreamingIntegrityMode
        inline constexpr uintptr_t StreamingMinRadius = 0x518;  // int
        inline constexpr uintptr_t StreamingPauseMode = 0x514;  // Enums::StreamingPauseMode
        inline constexpr uintptr_t StreamingTargetRadius = 0x51c;  // int
        inline constexpr uintptr_t ThrottleLevel = 0x520;  // int
        inline constexpr uintptr_t TouchEventsUseCollisionGroups = 0x524;  // Enums::RolloutState
        inline constexpr uintptr_t TouchesUseCollisionGroups = 0x3b8;  // bool
        inline constexpr uintptr_t UseInputSink = 0x52c;  // Enums::RolloutState
        inline constexpr uintptr_t UseNewLuauTypeSolver = 0x530;  // Enums::RolloutState
        inline constexpr uintptr_t ValidateEnabledProximityPrompt = 0x534;  // Enums::RolloutState
        inline constexpr uintptr_t WatermarkHash = 0x430;
    }
    namespace Camera {
        inline constexpr uintptr_t Rotation = 0xb8;  // nine floats, row-major; Position follows at +36
        inline constexpr uintptr_t Position = 0xdc;
        inline constexpr uintptr_t FieldOfView = 0x120;  // float, radians (vertical)
        inline constexpr uintptr_t CameraSubject = 0xa8;  // (object, control block) smart pointer pair
        inline constexpr uintptr_t CFrame = 0xb8;  // CoordinateFrame
        inline constexpr uintptr_t CameraType = 0x118;  // Enums::CameraTypeEnum::CameraType
        inline constexpr uintptr_t DiagonalFieldOfView = 0x11c;  // float
        inline constexpr uintptr_t FieldOfViewMode = 0x124;  // Enums::FieldOfViewMode
        inline constexpr uintptr_t Focus = 0xe8;  // CoordinateFrame
        inline constexpr uintptr_t HeadLocked = 0x144;  // bool
        inline constexpr uintptr_t HeadScale = 0x128;  // float
        inline constexpr uintptr_t MaxAxisFieldOfView = 0x12c;  // float
        inline constexpr uintptr_t OrthographicMode = 0x134;  // Enums::OrthographicMode
        inline constexpr uintptr_t OrthographicSize = 0x138;  // float
        inline constexpr uintptr_t ProjectionType = 0x13c;  // Enums::ProjectionType
        inline constexpr uintptr_t VRTiltAndRollEnabled = 0x145;  // bool
        inline constexpr uintptr_t ViewStretch = 0x140;  // float
    }
    namespace BasePart {
        inline constexpr uintptr_t Primitive = 0x168;
        inline constexpr uintptr_t AudioCanCollide = 0x117;  // bool
        inline constexpr uintptr_t CastShadow = 0x118;  // bool
        inline constexpr uintptr_t Elasticity = 0x260;  // float; at *(object + 0x168) + this
        inline constexpr uintptr_t Friction = 0x25c;  // float; at *(object + 0x168) + this
        inline constexpr uintptr_t LocalTransparencyModifier = 0xe8;  // float
        inline constexpr uintptr_t Locked = 0x119;  // bool
        inline constexpr uintptr_t Massless = 0x11a;  // bool
        inline constexpr uintptr_t Material = 0x24e;  // MaterialType; at *(object + 0x168) + this
        inline constexpr uintptr_t NetworkOwnershipRule = 0x26a;  // NetworkOwnership; at *(object + 0x168) + this
        inline constexpr uintptr_t Reflectance = 0xec;  // float
        inline constexpr uintptr_t Size = 0x1c4;  // Vector3; at *(object + 0x168) + this
        inline constexpr uintptr_t Transparency = 0x110;  // float
        inline constexpr uintptr_t size = 0x1c4;  // Vector3; at *(object + 0x168) + this
    }
    namespace Primitive {
        inline constexpr uintptr_t Rotation = 0xb0;  // nine floats, row-major; Position follows at +36
        inline constexpr uintptr_t Position = 0xd4;
        inline constexpr uintptr_t Flags = 0x1be;
        inline constexpr uintptr_t AssemblyLinearVelocity = 0xe0;  // copy refreshed from the solver body each physics step
    }
    namespace Humanoid {
        inline constexpr uintptr_t Health = 0x174;
        inline constexpr uintptr_t MaxHealth = 0x18c;
        inline constexpr uintptr_t WalkSpeed = 0x1b4;
        inline constexpr uintptr_t WalkSpeedCheck = 0x38c;  // must equal WalkSpeed
        inline constexpr uintptr_t JumpPower = 0x188;
        inline constexpr uintptr_t UseJumpPower = 0x1c6;  // bool
        inline constexpr uintptr_t AutoJumpEnabled = 0x1b8;  // bool
        inline constexpr uintptr_t AutoRotate = 0x1b9;  // bool
        inline constexpr uintptr_t AutomaticScalingEnabled = 0x1ba;  // bool
        inline constexpr uintptr_t BodyPartsCollidableOnDeath = 0x1bb;  // bool
        inline constexpr uintptr_t BreakJointsOnDeath = 0x1bc;  // bool
        inline constexpr uintptr_t CameraOffset = 0x100;  // Vector3
        inline constexpr uintptr_t CollisionType = 0x160;  // Enums::HumanoidCollisionTypeEnum::CollisionType
        inline constexpr uintptr_t DisplayDistanceType = 0x164;  // Enums::HumanoidDisplayDistanceTypeEnum::HumanoidDisplayDistanceType
        inline constexpr uintptr_t DisplayName = 0xa0;
        inline constexpr uintptr_t EvaluateStateMachine = 0x1bd;  // bool
        inline constexpr uintptr_t FinishedState = 0x1be;  // bool
        inline constexpr uintptr_t HealthDisplayDistance = 0x16c;  // float
        inline constexpr uintptr_t HealthDisplayType = 0x170;  // Enums::HumanoidHealthDisplayTypeEnum::HumanoidHealthDisplayType
        inline constexpr uintptr_t Health_XML = 0x174;  // float
        inline constexpr uintptr_t HipHeight = 0x178;  // float
        inline constexpr uintptr_t InternalAvatarRulesRootPartSize = 0x10c;  // Vector3
        inline constexpr uintptr_t InternalAvatarRulesRootPartSizeScalesWithBody = 0x1bf;  // bool
        inline constexpr uintptr_t InternalBodyScale = 0x118;  // Vector3
        inline constexpr uintptr_t InternalDisplayName = 0xb8;
        inline constexpr uintptr_t InternalHeadScale = 0x17c;  // float
        inline constexpr uintptr_t InternalOriginalHipHeight = 0x180;  // float
        inline constexpr uintptr_t Jump = 0x1c0;  // bool
        inline constexpr uintptr_t JumpHeight = 0x184;  // float
        inline constexpr uintptr_t JumpReplicate = 0x1c0;  // bool
        inline constexpr uintptr_t MaxSlopeAngle = 0x190;  // float
        inline constexpr uintptr_t MoveDirectionInternal = 0x124;  // Vector3
        inline constexpr uintptr_t NameDisplayDistance = 0x194;  // float
        inline constexpr uintptr_t NameOcclusion = 0x198;  // Enums::NameOcclusionEnum::NameOcclusion
        inline constexpr uintptr_t NetworkHumanoidState = 0x19c;  // HUMAN::StateType
        inline constexpr uintptr_t NoFloorTimerState = 0x1a0;  // float
        inline constexpr uintptr_t OverrideDefaultCollisions = 0x1c1;  // bool
        inline constexpr uintptr_t PlatformStand = 0x1c2;  // bool
        inline constexpr uintptr_t RequiresNeck = 0x1c3;  // bool
        inline constexpr uintptr_t RigType = 0x1a4;  // HumanoidRigType
        inline constexpr uintptr_t RotationType = 0x1a8;  // Enums::RotationTypeEnum::RotationType
        inline constexpr uintptr_t Sit = 0x1c4;  // bool
        inline constexpr uintptr_t Strafe = 0x1c5;  // bool
        inline constexpr uintptr_t TargetPoint = 0x130;  // Vector3
        inline constexpr uintptr_t TimerState = 0x1ac;  // float
        inline constexpr uintptr_t WalkAngleError = 0x1b0;  // float
        inline constexpr uintptr_t WalkDirection = 0x13c;  // Vector3
        inline constexpr uintptr_t WalkToPart = 0xf0;
        inline constexpr uintptr_t WalkToPoint = 0x148;  // Vector3
        inline constexpr uintptr_t maxHealth = 0x18c;  // float
    }
    namespace PrimitiveFlags {
        inline constexpr uintptr_t CanCollide = 0x8;  // bit mask in Primitive::Flags (a byte)
    }
    namespace SolverBody {
        inline constexpr uintptr_t Pointer = 0x140;  // Primitive -> solver body that physics integrates
        inline constexpr uintptr_t Position = 0x98;  // Vector3; copies follow every BlockStride bytes
        inline constexpr uintptr_t Velocity = 0xa4;  // Vector3; write here to change motion mid-air
        inline constexpr uintptr_t BlockStride = 0x48;  // bytes between (position, velocity) copies
    }
    namespace Accessory {
        inline constexpr uintptr_t AccessoryType = 0x158;  // AccessoryType
    }
    namespace AccessoryDescription {
        inline constexpr uintptr_t AccessoryType = 0xd4;  // AccessoryType
        inline constexpr uintptr_t AssetId = 0xa8;  // int64
        inline constexpr uintptr_t Instance = 0x98;
        inline constexpr uintptr_t IsLayered = 0xe0;  // bool
        inline constexpr uintptr_t Order = 0xd8;  // int
        inline constexpr uintptr_t Position = 0xb0;  // Vector3
        inline constexpr uintptr_t Puffiness = 0xdc;  // float
        inline constexpr uintptr_t Rotation = 0xbc;  // Vector3
        inline constexpr uintptr_t Scale = 0xc8;  // Vector3
    }
    namespace Accoutrement {
        inline constexpr uintptr_t AttachmentForward = 0xa8;  // Vector3
        inline constexpr uintptr_t AttachmentPoint = 0xa0;  // CoordinateFrame
        inline constexpr uintptr_t AttachmentPos = 0xc4;  // Vector3
        inline constexpr uintptr_t AttachmentRight = 0xa0;  // Vector3
        inline constexpr uintptr_t AttachmentUp = 0xa4;  // Vector3
        inline constexpr uintptr_t BackendAccoutrementState = 0xd0;  // int
    }
    namespace Ads_AdGui {
        inline constexpr uintptr_t AdShape = 0x7c0;
        inline constexpr uintptr_t EnableVideoAds = 0x7c4;  // bool
    }
    namespace Ads_AdPlacement {
        inline constexpr uintptr_t AdFormat = 0x108;
        inline constexpr uintptr_t PlacementId = 0x100;  // int64
    }
    namespace AirController {
        inline constexpr uintptr_t BalanceMaxTorque = 0xcc;  // float
        inline constexpr uintptr_t BalanceSpeed = 0xd0;  // float
        inline constexpr uintptr_t LinearImpulse = 0xc0;  // Vector3
        inline constexpr uintptr_t MaintainAngularMomentum = 0xe0;  // bool
        inline constexpr uintptr_t MaintainLinearMomentum = 0xe1;  // bool
        inline constexpr uintptr_t MoveMaxForce = 0xd4;  // float
        inline constexpr uintptr_t TurnMaxTorque = 0xd8;  // float
        inline constexpr uintptr_t TurnSpeedFactor = 0xdc;  // float
    }
    namespace AnalyticsService {
        inline constexpr uintptr_t ApiKey = 0xb0;
    }
    namespace AnimationClip {
        inline constexpr uintptr_t Loop = 0xb4;  // bool
        inline constexpr uintptr_t Priority = 0xa0;  // AnimationPriority
    }
    namespace AnimationNodeDefinition {
        inline constexpr uintptr_t NodeId = 0x98;
        inline constexpr uintptr_t NodeType = 0xb8;  // Enums::AnimationNodeType
    }
    namespace AnimationPlayer {
        inline constexpr uintptr_t AutoPlay = 0xf8;  // bool
        inline constexpr uintptr_t CurrentFrame = 0xf0;  // int
        inline constexpr uintptr_t Enabled = 0xf9;  // bool
        inline constexpr uintptr_t Loop = 0xfb;  // bool
        inline constexpr uintptr_t Speed = 0xf4;  // float
        inline constexpr uintptr_t TimePosition = 0xe8;  // double
        inline constexpr uintptr_t Track = 0xc0;
    }
    namespace AnimationTrack {
        inline constexpr uintptr_t TimePosition = 0xc0;  // float
    }
    namespace AnimationValueNodeDefinition {
        inline constexpr uintptr_t NodeId = 0x98;
        inline constexpr uintptr_t NodeType = 0xb0;  // Enums::AnimationValueNodeType
    }
    namespace Animator {
        inline constexpr uintptr_t AnimTrackMetadata0 = 0x38c;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata1 = 0x390;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata10 = 0x394;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata11 = 0x398;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata12 = 0x39c;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata13 = 0x3a0;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata14 = 0x3a4;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata15 = 0x3a8;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata2 = 0x3ac;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata3 = 0x3b0;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata4 = 0x3b4;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata5 = 0x3b8;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata6 = 0x3bc;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata7 = 0x3c0;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata8 = 0x3c4;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackMetadata9 = 0x3c8;  // AnimTrackMetadata
        inline constexpr uintptr_t AnimTrackPlayState0 = 0xd8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState1 = 0xe8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState10 = 0xf8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState11 = 0x108;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState12 = 0x118;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState13 = 0x128;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState14 = 0x138;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState15 = 0x148;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState2 = 0x158;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState3 = 0x168;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState4 = 0x178;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState5 = 0x188;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState6 = 0x198;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState7 = 0x1a8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState8 = 0x1b8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackPlayState9 = 0x1c8;  // AnimTrackPlayState
        inline constexpr uintptr_t AnimTrackWeight0 = 0x1d8;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight1 = 0x1e8;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight10 = 0x1f8;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight11 = 0x208;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight12 = 0x218;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight13 = 0x228;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight14 = 0x238;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight15 = 0x248;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight2 = 0x258;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight3 = 0x268;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight4 = 0x278;  // AnimTrackWeight
        inline constexpr uintptr_t AnimTrackWeight5 = 0x288;  // AnimTrackWeight
        inline constexpr uintptr_t AnimationId0 = 0x2d8;  // int64
        inline constexpr uintptr_t AnimationId1 = 0x2e0;  // int64
        inline constexpr uintptr_t AnimationId10 = 0x2e8;  // int64
        inline constexpr uintptr_t AnimationId11 = 0x2f0;  // int64
        inline constexpr uintptr_t AnimationId12 = 0x2f8;  // int64
        inline constexpr uintptr_t AnimationId13 = 0x300;  // int64
        inline constexpr uintptr_t AnimationId14 = 0x308;  // int64
        inline constexpr uintptr_t AnimationId15 = 0x310;  // int64
        inline constexpr uintptr_t AnimationId2 = 0x318;  // int64
        inline constexpr uintptr_t AnimationId3 = 0x320;  // int64
        inline constexpr uintptr_t AnimationId4 = 0x328;  // int64
        inline constexpr uintptr_t AnimationId5 = 0x330;  // int64
        inline constexpr uintptr_t AnimationId6 = 0x338;  // int64
        inline constexpr uintptr_t AnimationId7 = 0x340;  // int64
        inline constexpr uintptr_t AnimationId8 = 0x348;  // int64
        inline constexpr uintptr_t AnimationId9 = 0x350;  // int64
        inline constexpr uintptr_t PreferLodEnabled = 0x3cc;  // bool
    }
    namespace ArcHandles {
        inline constexpr uintptr_t Axes = 0x104;  // Axes
        inline constexpr uintptr_t MouseButton1DownConnectionCount = 0x108;  // int
        inline constexpr uintptr_t MouseButton1UpConnectionCount = 0x10c;  // int
        inline constexpr uintptr_t MouseDragConnectionCount = 0x110;  // int
        inline constexpr uintptr_t MouseEnterConnectionCount = 0x114;  // int
        inline constexpr uintptr_t MouseLeaveConnectionCount = 0x118;  // int
    }
    namespace AssetDeliveryProxy {
        inline constexpr uintptr_t Interface = 0xb0;
        inline constexpr uintptr_t StartServer = 0xcc;  // bool
    }
    namespace AssetPatchSettings {
        inline constexpr uintptr_t ContentId = 0x98;
        inline constexpr uintptr_t OutputPath = 0xb0;
        inline constexpr uintptr_t PatchId = 0xc8;
    }
    namespace AssetService {
        inline constexpr uintptr_t AllowInsertFreeAssets = 0xa1;  // bool
    }
    namespace Atmosphere {
        inline constexpr uintptr_t Color = 0xa0;  // Color3
        inline constexpr uintptr_t Decay = 0xac;  // Color3
        inline constexpr uintptr_t Density = 0xb8;  // float
        inline constexpr uintptr_t Glare = 0xbc;  // float
        inline constexpr uintptr_t Haze = 0xc0;  // float
        inline constexpr uintptr_t Offset = 0xc4;  // float
    }
    namespace Attachment {
        inline constexpr uintptr_t Axis = 0xa0;  // Vector3
        inline constexpr uintptr_t CFrame = 0xa0;  // CoordinateFrame
        inline constexpr uintptr_t Position = 0xac;  // Vector3
        inline constexpr uintptr_t SecondaryAxis = 0xb8;  // Vector3
        inline constexpr uintptr_t Visible = 0xc4;  // bool
    }
    namespace AudioSearchParams {
        inline constexpr uintptr_t Album = 0xa0;
        inline constexpr uintptr_t Artist = 0xb8;
        inline constexpr uintptr_t AudioSubType = 0x118;  // AudioSubType
        inline constexpr uintptr_t AudioSubtype = 0x118;  // AudioSubType
        inline constexpr uintptr_t MaxDuration = 0x11c;  // int
        inline constexpr uintptr_t MaxPageSize = 0x120;  // int
        inline constexpr uintptr_t MinDuration = 0x124;  // int
        inline constexpr uintptr_t SearchKeyword = 0xd0;
        inline constexpr uintptr_t SortType = 0x128;  // AudioSortType
        inline constexpr uintptr_t Tag = 0xe8;
        inline constexpr uintptr_t Title = 0x100;
    }
    namespace AuroraScript {
        inline constexpr uintptr_t EnableCulling = 0x120;  // bool
        inline constexpr uintptr_t EnableLOD = 0x121;  // bool
        inline constexpr uintptr_t LODCriticality = 0x118;  // int
        inline constexpr uintptr_t Priority = 0x11c;  // int
    }
    namespace AuroraScriptObject {
        inline constexpr uintptr_t FrameId = 0xb8;  // int
        inline constexpr uintptr_t LODLevel = 0xbc;  // int
        inline constexpr uintptr_t MaxFrequency = 0xc0;  // int
        inline constexpr uintptr_t PriorFrameInvoked = 0xc4;  // int
    }
    namespace AuroraService {
        inline constexpr uintptr_t BufferFullInputCount = 0xc8;  // int
        inline constexpr uintptr_t HashRoundingPoint = 0xb8;  // double
        inline constexpr uintptr_t IgnoreRotation = 0xdc;  // bool
        inline constexpr uintptr_t InputDropRate = 0xcc;  // float
        inline constexpr uintptr_t LockStepIdOffset = 0xdd;  // bool
        inline constexpr uintptr_t OutOfOrderInputCount = 0xd0;  // int
        inline constexpr uintptr_t RCCHeartbeatFPS = 0xc0;  // double
        inline constexpr uintptr_t RollbackOffset = 0xd4;  // int
        inline constexpr uintptr_t TooOldInputCount = 0xd8;  // int
    }
    namespace AvatarAbilityRules {
        inline constexpr uintptr_t CharacterControllerMode = 0x98;  // Enums::AvatarSettingsCharacterControllerMode
        inline constexpr uintptr_t EnableClimbing = 0x9c;  // bool
        inline constexpr uintptr_t EnableCrouching = 0x9d;  // bool
        inline constexpr uintptr_t EnableFallingDown = 0x9e;  // bool
        inline constexpr uintptr_t EnableGettingUp = 0x9f;  // bool
        inline constexpr uintptr_t EnableHolding = 0xa0;  // bool
        inline constexpr uintptr_t EnableJumping = 0xa1;  // bool
        inline constexpr uintptr_t EnableReaching = 0xa2;  // bool
        inline constexpr uintptr_t EnableRunning = 0xa3;  // bool
        inline constexpr uintptr_t EnableSitting = 0xa4;  // bool
        inline constexpr uintptr_t EnableSprinting = 0xa5;  // bool
        inline constexpr uintptr_t EnableSwimming = 0xa6;  // bool
        inline constexpr uintptr_t EnableTurning = 0xa7;  // bool
    }
    namespace AvatarAccessoryRules {
        inline constexpr uintptr_t AccessoryMode = 0x124;  // Enums::AvatarSettingsAccessoryMode
        inline constexpr uintptr_t BackAccessoryOverride = 0x98;  // int64
        inline constexpr uintptr_t CustomAccessoryMode = 0x128;  // Enums::AvatarSettingsCustomAccessoryMode
        inline constexpr uintptr_t CustomBackAccessoryEnabled = 0x130;  // bool
        inline constexpr uintptr_t CustomBackAccessoryId = 0xa0;  // int64
        inline constexpr uintptr_t CustomFaceAccessoryEnabled = 0x131;  // bool
        inline constexpr uintptr_t CustomFaceAccessoryId = 0xa8;  // int64
        inline constexpr uintptr_t CustomFrontAccessoryEnabled = 0x132;  // bool
        inline constexpr uintptr_t CustomFrontAccessoryId = 0xb0;  // int64
        inline constexpr uintptr_t CustomHairAccessoryEnabled = 0x133;  // bool
        inline constexpr uintptr_t CustomHairAccessoryId = 0xb8;  // int64
        inline constexpr uintptr_t CustomHeadAccessoryEnabled = 0x134;  // bool
        inline constexpr uintptr_t CustomHeadAccessoryId = 0xc0;  // int64
        inline constexpr uintptr_t CustomNeckAccessoryEnabled = 0x135;  // bool
        inline constexpr uintptr_t CustomNeckAccessoryId = 0xc8;  // int64
        inline constexpr uintptr_t CustomShoulderAccessoryEnabled = 0x136;  // bool
        inline constexpr uintptr_t CustomShoulderAccessoryId = 0xd0;  // int64
        inline constexpr uintptr_t CustomWaistAccessoryEnabled = 0x137;  // bool
        inline constexpr uintptr_t CustomWaistAccessoryId = 0xd8;  // int64
        inline constexpr uintptr_t EnableEmissives = 0x138;  // bool
        inline constexpr uintptr_t EnableSound = 0x139;  // bool
        inline constexpr uintptr_t EnableVFX = 0x13a;  // bool
        inline constexpr uintptr_t FaceAccessoryOverride = 0xe0;  // int64
        inline constexpr uintptr_t FrontAccessoryOverride = 0xe8;  // int64
        inline constexpr uintptr_t HairAccessoryOverride = 0xf0;  // int64
        inline constexpr uintptr_t HeadAccessoryOverride = 0xf8;  // int64
        inline constexpr uintptr_t LimitBounds = 0x118;  // Vector3
        inline constexpr uintptr_t LimitMethod = 0x12c;  // Enums::AvatarSettingsAccessoryLimitMethod
        inline constexpr uintptr_t NeckAccessoryOverride = 0x100;  // int64
        inline constexpr uintptr_t ShoulderAccessoryOverride = 0x108;  // int64
        inline constexpr uintptr_t WaistAccessoryOverride = 0x110;  // int64
    }
    namespace AvatarAnimationRules {
        inline constexpr uintptr_t AnimationClipsMode = 0x138;  // Enums::AvatarSettingsAnimationClipsMode
        inline constexpr uintptr_t AnimationPacksMode = 0x13c;  // Enums::AvatarSettingsAnimationPacksMode
        inline constexpr uintptr_t ClimbAnimationOverride = 0x98;  // int64
        inline constexpr uintptr_t CustomClimbAnimationEnabled = 0x140;  // bool
        inline constexpr uintptr_t CustomClimbAnimationId = 0xa0;  // int64
        inline constexpr uintptr_t CustomFallAnimationEnabled = 0x141;  // bool
        inline constexpr uintptr_t CustomFallAnimationId = 0xa8;  // int64
        inline constexpr uintptr_t CustomIdleAlt1AnimationEnabled = 0x142;  // bool
        inline constexpr uintptr_t CustomIdleAlt1AnimationId = 0xb0;  // int64
        inline constexpr uintptr_t CustomIdleAlt2AnimationEnabled = 0x143;  // bool
        inline constexpr uintptr_t CustomIdleAlt2AnimationId = 0xb8;  // int64
        inline constexpr uintptr_t CustomIdleAnimationEnabled = 0x144;  // bool
        inline constexpr uintptr_t CustomIdleAnimationId = 0xc0;  // int64
        inline constexpr uintptr_t CustomJumpAnimationEnabled = 0x145;  // bool
        inline constexpr uintptr_t CustomJumpAnimationId = 0xc8;  // int64
        inline constexpr uintptr_t CustomRunAnimationEnabled = 0x146;  // bool
        inline constexpr uintptr_t CustomRunAnimationId = 0xd0;  // int64
        inline constexpr uintptr_t CustomSwimAnimationEnabled = 0x147;  // bool
        inline constexpr uintptr_t CustomSwimAnimationId = 0xd8;  // int64
        inline constexpr uintptr_t CustomSwimIdleAnimationEnabled = 0x148;  // bool
        inline constexpr uintptr_t CustomSwimIdleAnimationId = 0xe0;  // int64
        inline constexpr uintptr_t CustomWalkAnimationEnabled = 0x149;  // bool
        inline constexpr uintptr_t CustomWalkAnimationId = 0xe8;  // int64
        inline constexpr uintptr_t FallAnimationOverride = 0xf0;  // int64
        inline constexpr uintptr_t IdleAltAnimationOverride = 0xf8;  // int64
        inline constexpr uintptr_t IdleAnimationOverride = 0x100;  // int64
        inline constexpr uintptr_t JumpAnimationOverride = 0x108;  // int64
        inline constexpr uintptr_t MoodAnimationOverride = 0x110;  // int64
        inline constexpr uintptr_t RunAnimationOverride = 0x118;  // int64
        inline constexpr uintptr_t SwimAnimationOverride = 0x120;  // int64
        inline constexpr uintptr_t SwimIdleAnimationOverride = 0x128;  // int64
        inline constexpr uintptr_t WalkAnimationOverride = 0x130;  // int64
    }
    namespace AvatarBodyRules {
        inline constexpr uintptr_t AppearanceMode = 0x150;  // Enums::AvatarSettingsAppearanceMode
        inline constexpr uintptr_t AvatarType = 0x154;  // GameAvatarType
        inline constexpr uintptr_t BuildMode = 0x158;  // Enums::AvatarSettingsBuildMode
        inline constexpr uintptr_t CustomBodyBundleId = 0x98;  // int64
        inline constexpr uintptr_t CustomBodyType = 0x15c;  // Enums::AvatarSettingsCustomBodyType
        inline constexpr uintptr_t CustomBodyTypeScale = 0x120;  // NumberRange
        inline constexpr uintptr_t CustomBuildBodyType = 0x120;  // NumberRange
        inline constexpr uintptr_t CustomBuildHead = 0x128;  // NumberRange
        inline constexpr uintptr_t CustomBuildHeight = 0x130;  // NumberRange
        inline constexpr uintptr_t CustomBuildProportions = 0x138;  // NumberRange
        inline constexpr uintptr_t CustomBuildWidth = 0x140;  // NumberRange
        inline constexpr uintptr_t CustomEyebrowEnabled = 0x164;  // bool
        inline constexpr uintptr_t CustomEyebrowId = 0xa0;  // int64
        inline constexpr uintptr_t CustomEyelashEnabled = 0x165;  // bool
        inline constexpr uintptr_t CustomEyelashId = 0xa8;  // int64
        inline constexpr uintptr_t CustomFaceEnabled = 0x166;  // bool
        inline constexpr uintptr_t CustomFaceId = 0xb0;  // int64
        inline constexpr uintptr_t CustomHeadEnabled = 0x167;  // bool
        inline constexpr uintptr_t CustomHeadId = 0xb8;  // int64
        inline constexpr uintptr_t CustomHeadScale = 0x128;  // NumberRange
        inline constexpr uintptr_t CustomHeight = 0x148;  // NumberRange
        inline constexpr uintptr_t CustomHeightScale = 0x130;  // NumberRange
        inline constexpr uintptr_t CustomLeftArmEnabled = 0x168;  // bool
        inline constexpr uintptr_t CustomLeftArmId = 0xc0;  // int64
        inline constexpr uintptr_t CustomLeftLegEnabled = 0x169;  // bool
        inline constexpr uintptr_t CustomLeftLegId = 0xc8;  // int64
        inline constexpr uintptr_t CustomMoodEnabled = 0x16a;  // bool
        inline constexpr uintptr_t CustomMoodId = 0xd0;  // int64
        inline constexpr uintptr_t CustomProportionsScale = 0x138;  // NumberRange
        inline constexpr uintptr_t CustomRightArmEnabled = 0x16b;  // bool
        inline constexpr uintptr_t CustomRightArmId = 0xd8;  // int64
        inline constexpr uintptr_t CustomRightLegEnabled = 0x16c;  // bool
        inline constexpr uintptr_t CustomRightLegId = 0xe0;  // int64
        inline constexpr uintptr_t CustomTorsoEnabled = 0x16d;  // bool
        inline constexpr uintptr_t CustomTorsoId = 0xe8;  // int64
        inline constexpr uintptr_t CustomWidthScale = 0x140;  // NumberRange
        inline constexpr uintptr_t CustomWorldHeight = 0x148;  // NumberRange
        inline constexpr uintptr_t HeadOverride = 0xf0;  // int64
        inline constexpr uintptr_t KeepPlayerHead = 0x16e;  // bool
        inline constexpr uintptr_t LeftArmOverride = 0xf8;  // int64
        inline constexpr uintptr_t LeftLegOverride = 0x100;  // int64
        inline constexpr uintptr_t RightArmOverride = 0x108;  // int64
        inline constexpr uintptr_t RightLegOverride = 0x110;  // int64
        inline constexpr uintptr_t ScaleMode = 0x160;  // Enums::AvatarSettingsScaleMode
        inline constexpr uintptr_t TorsoOverride = 0x118;  // int64
    }
    namespace AvatarClothingRules {
        inline constexpr uintptr_t ClassicPantsOverride = 0x98;  // int64
        inline constexpr uintptr_t ClassicShirtOverride = 0xa0;  // int64
        inline constexpr uintptr_t ClassicTShirtOverride = 0xa8;  // int64
        inline constexpr uintptr_t ClothingMode = 0x164;  // Enums::AvatarSettingsClothingMode
        inline constexpr uintptr_t CustomClassicPantsAccessoryEnabled = 0x16c;  // bool
        inline constexpr uintptr_t CustomClassicPantsAccessoryId = 0xb0;  // int64
        inline constexpr uintptr_t CustomClassicShirtsAccessoryEnabled = 0x16d;  // bool
        inline constexpr uintptr_t CustomClassicShirtsAccessoryId = 0xb8;  // int64
        inline constexpr uintptr_t CustomClassicTShirtsAccessoryEnabled = 0x16e;  // bool
        inline constexpr uintptr_t CustomClassicTShirtsAccessoryId = 0xc0;  // int64
        inline constexpr uintptr_t CustomClothingMode = 0x168;  // Enums::AvatarSettingsCustomClothingMode
        inline constexpr uintptr_t CustomDressSkirtAccessoryEnabled = 0x16f;  // bool
        inline constexpr uintptr_t CustomDressSkirtAccessoryId = 0xc8;  // int64
        inline constexpr uintptr_t CustomJacketAccessoryEnabled = 0x170;  // bool
        inline constexpr uintptr_t CustomJacketAccessoryId = 0xd0;  // int64
        inline constexpr uintptr_t CustomLeftShoesAccessoryEnabled = 0x171;  // bool
        inline constexpr uintptr_t CustomLeftShoesAccessoryId = 0xd8;  // int64
        inline constexpr uintptr_t CustomPantsAccessoryEnabled = 0x172;  // bool
        inline constexpr uintptr_t CustomPantsAccessoryId = 0xe0;  // int64
        inline constexpr uintptr_t CustomRightShoesAccessoryEnabled = 0x173;  // bool
        inline constexpr uintptr_t CustomRightShoesAccessoryId = 0xe8;  // int64
        inline constexpr uintptr_t CustomShirtAccessoryEnabled = 0x174;  // bool
        inline constexpr uintptr_t CustomShirtAccessoryId = 0xf0;  // int64
        inline constexpr uintptr_t CustomShortsAccessoryEnabled = 0x175;  // bool
        inline constexpr uintptr_t CustomShortsAccessoryId = 0xf8;  // int64
        inline constexpr uintptr_t CustomSweaterAccessoryEnabled = 0x176;  // bool
        inline constexpr uintptr_t CustomSweaterAccessoryId = 0x100;  // int64
        inline constexpr uintptr_t CustomTShirtAccessoryEnabled = 0x177;  // bool
        inline constexpr uintptr_t CustomTShirtAccessoryId = 0x108;  // int64
        inline constexpr uintptr_t DressSkirtAccessoryOverride = 0x110;  // int64
        inline constexpr uintptr_t JacketAccessoryOverride = 0x118;  // int64
        inline constexpr uintptr_t LeftShoeAccessoryOverride = 0x120;  // int64
        inline constexpr uintptr_t LimitBounds = 0x158;  // Vector3
        inline constexpr uintptr_t PantsAccessoryOverride = 0x128;  // int64
        inline constexpr uintptr_t RightShoeAccessoryOverride = 0x130;  // int64
        inline constexpr uintptr_t ShirtAccessoryOverride = 0x138;  // int64
        inline constexpr uintptr_t ShortsAccessoryOverride = 0x140;  // int64
        inline constexpr uintptr_t SweaterAccessoryOverride = 0x148;  // int64
        inline constexpr uintptr_t TShirtAccessoryOverride = 0x150;  // int64
    }
    namespace AvatarCollisionRules {
        inline constexpr uintptr_t BodyPartsCollidableOnDeath = 0xb0;  // bool
        inline constexpr uintptr_t CollisionMode = 0xa4;  // Enums::AvatarSettingsCollisionMode
        inline constexpr uintptr_t HitAndTouchDetectionMode = 0xa8;  // Enums::AvatarSettingsHitAndTouchDetectionMode
        inline constexpr uintptr_t LegacyCollisionMode = 0xac;  // Enums::AvatarSettingsLegacyCollisionMode
        inline constexpr uintptr_t SingleColliderSize = 0x98;  // Vector3
    }
    namespace AvatarRules {
        inline constexpr uintptr_t AvatarType = 0x98;  // GameAvatarType
    }
    namespace AvatarSettings {
        inline constexpr uintptr_t Loaded = 0xcc;  // bool
        inline constexpr uintptr_t RulesSchemaVersion = 0xc8;  // int
    }
    namespace BaseCoreGuiConfiguration {
        inline constexpr uintptr_t Enabled = 0x95;  // bool
    }
    namespace BaseScript {
        inline constexpr uintptr_t Disabled = 0x10c;  // bool
        inline constexpr uintptr_t LinkedSource = 0xe8;  // ContentId
        inline constexpr uintptr_t RunContext = 0x108;  // Enums::RunContext
    }
    namespace BaseWrap {
        inline constexpr uintptr_t CageMeshContent = 0xa0;  // Content
        inline constexpr uintptr_t CageOrigin = 0x130;  // CoordinateFrame
        inline constexpr uintptr_t HSRData = 0x120;  // SharedString
        inline constexpr uintptr_t HSRMeshIdData = 0x128;  // SharedString
        inline constexpr uintptr_t ImportInProcess = 0x190;  // bool
        inline constexpr uintptr_t ImportOrigin = 0x160;  // CoordinateFrame
    }
    namespace Beam {
        inline constexpr uintptr_t Brightness = 0x160;  // float
        inline constexpr uintptr_t Color = 0xe0;  // ColorSequence
        inline constexpr uintptr_t CurveSize0 = 0x164;  // float
        inline constexpr uintptr_t CurveSize1 = 0x168;  // float
        inline constexpr uintptr_t Enabled = 0x194;  // bool
        inline constexpr uintptr_t FaceCamera = 0x195;  // bool
        inline constexpr uintptr_t LightEmission = 0x16c;  // float
        inline constexpr uintptr_t LightInfluence = 0x170;  // float
        inline constexpr uintptr_t LocalTransparencyModifier = 0x174;  // float
        inline constexpr uintptr_t Segments = 0x178;  // int
        inline constexpr uintptr_t TextureLength = 0x17c;  // float
        inline constexpr uintptr_t TextureMode = 0x180;  // TextureMode
        inline constexpr uintptr_t TextureSpeed = 0x184;  // float
        inline constexpr uintptr_t Transparency = 0xa0;  // NumberSequence
        inline constexpr uintptr_t Width0 = 0x188;  // float
        inline constexpr uintptr_t Width1 = 0x18c;  // float
        inline constexpr uintptr_t ZOffset = 0x190;  // float
    }
    namespace BevelMesh {
        inline constexpr uintptr_t Bevel = 0xc4;  // float
        inline constexpr uintptr_t Bevel Roundness = 0xc8;  // float
        inline constexpr uintptr_t Bulge = 0xcc;  // float
    }
    namespace BillboardGui {
        inline constexpr uintptr_t Active = 0x71c;  // bool
        inline constexpr uintptr_t AlwaysOnTop = 0x71d;  // bool
        inline constexpr uintptr_t Brightness = 0x700;  // float
        inline constexpr uintptr_t ClipsDescendants = 0x71e;  // bool
        inline constexpr uintptr_t DistanceLowerLimit = 0x708;  // float
        inline constexpr uintptr_t DistanceStep = 0x70c;  // float
        inline constexpr uintptr_t DistanceUpperLimit = 0x710;  // float
        inline constexpr uintptr_t ExtentsOffset = 0x6c8;  // Vector3
        inline constexpr uintptr_t ExtentsOffsetWorldSpace = 0x6d4;  // Vector3
        inline constexpr uintptr_t LightInfluence = 0x714;  // float
        inline constexpr uintptr_t MaxDistance = 0x718;  // float
        inline constexpr uintptr_t Size = 0x6b8;  // UDim2
        inline constexpr uintptr_t SizeOffset = 0x6f8;  // Vector2
        inline constexpr uintptr_t StudsOffset = 0x6e0;  // Vector3
        inline constexpr uintptr_t StudsOffsetWorldSpace = 0x6ec;  // Vector3
    }
    namespace BinaryStringValue {
        inline constexpr uintptr_t Value = 0xa0;  // BinaryString
    }
    namespace BloomEffect {
        inline constexpr uintptr_t Intensity = 0x98;  // float
        inline constexpr uintptr_t Size = 0x9c;  // float
        inline constexpr uintptr_t Threshold = 0xa0;  // float
    }
    namespace BlurEffect {
        inline constexpr uintptr_t Size = 0x98;  // float
    }
    namespace BodyAngularVelocity {
        inline constexpr uintptr_t AngularVelocity = 0x278;  // Vector3
        inline constexpr uintptr_t MaxTorque = 0x284;  // Vector3
        inline constexpr uintptr_t P = 0x290;  // float
        inline constexpr uintptr_t angularvelocity = 0x278;  // Vector3
        inline constexpr uintptr_t maxTorque = 0x284;  // Vector3
    }
    namespace BodyColors {
        inline constexpr uintptr_t HeadColor = 0xa8;  // BrickColor
        inline constexpr uintptr_t HeadColor3 = 0xac;  // Color3
        inline constexpr uintptr_t LeftArmColor = 0xb8;  // BrickColor
        inline constexpr uintptr_t LeftArmColor3 = 0xbc;  // Color3
        inline constexpr uintptr_t LeftLegColor = 0xc8;  // BrickColor
        inline constexpr uintptr_t LeftLegColor3 = 0xcc;  // Color3
        inline constexpr uintptr_t RightArmColor = 0xd8;  // BrickColor
        inline constexpr uintptr_t RightArmColor3 = 0xdc;  // Color3
        inline constexpr uintptr_t RightLegColor = 0xe8;  // BrickColor
        inline constexpr uintptr_t RightLegColor3 = 0xec;  // Color3
        inline constexpr uintptr_t TorsoColor = 0xf8;  // BrickColor
        inline constexpr uintptr_t TorsoColor3 = 0xfc;  // Color3
    }
    namespace BodyGyro {
        inline constexpr uintptr_t D = 0x2b4;  // float
        inline constexpr uintptr_t MaxTorque = 0x2a8;  // Vector3
        inline constexpr uintptr_t P = 0x2b8;  // float
        inline constexpr uintptr_t maxTorque = 0x2a8;  // Vector3
    }
    namespace BodyPartDescription {
        inline constexpr uintptr_t AssetId = 0xc0;  // int64
        inline constexpr uintptr_t BodyPart = 0xd4;  // BodyPart
        inline constexpr uintptr_t Color = 0xc8;  // Color3
        inline constexpr uintptr_t HeadShape = 0x98;
        inline constexpr uintptr_t Instance = 0xb0;
    }
    namespace BodyPosition {
        inline constexpr uintptr_t D = 0x290;  // float
        inline constexpr uintptr_t MaxForce = 0x278;  // Vector3
        inline constexpr uintptr_t P = 0x294;  // float
        inline constexpr uintptr_t Position = 0x284;  // Vector3
        inline constexpr uintptr_t maxForce = 0x278;  // Vector3
        inline constexpr uintptr_t position = 0x284;  // Vector3
    }
    namespace BodyThrust {
        inline constexpr uintptr_t Force = 0x270;  // Vector3
        inline constexpr uintptr_t Location = 0x27c;  // Vector3
        inline constexpr uintptr_t force = 0x270;  // Vector3
        inline constexpr uintptr_t location = 0x27c;  // Vector3
    }
    namespace BodyVelocity {
        inline constexpr uintptr_t MaxForce = 0x278;  // Vector3
        inline constexpr uintptr_t P = 0x290;  // float
        inline constexpr uintptr_t Velocity = 0x284;  // Vector3
        inline constexpr uintptr_t maxForce = 0x278;  // Vector3
        inline constexpr uintptr_t velocity = 0x284;  // Vector3
    }
    namespace BoneInstance {
        inline constexpr uintptr_t Transform = 0x168;  // CoordinateFrame
    }
    namespace BoolValue {
        inline constexpr uintptr_t Value = 0xa0;  // bool
    }
    namespace BoxHandleAdornment {
        inline constexpr uintptr_t DoubleSided = 0x19c;  // bool
        inline constexpr uintptr_t Shading = 0x198;  // Enums::AdornShading
        inline constexpr uintptr_t Size = 0x18c;  // Vector3
    }
    namespace BrickColorValue {
        inline constexpr uintptr_t Value = 0xa0;  // BrickColor
    }
    namespace BubbleChatConfiguration {
        inline constexpr uintptr_t AdorneeName = 0xa0;
        inline constexpr uintptr_t BackgroundColor3 = 0xd0;  // Color3
        inline constexpr uintptr_t BackgroundTransparency = 0xb8;  // double
        inline constexpr uintptr_t BubbleDuration = 0xf4;  // float
        inline constexpr uintptr_t BubblesSpacing = 0xf8;  // float
        inline constexpr uintptr_t Enabled = 0x10c;  // bool
        inline constexpr uintptr_t LocalPlayerStudsOffset = 0xdc;  // Vector3
        inline constexpr uintptr_t MaxBubbles = 0xfc;  // float
        inline constexpr uintptr_t MaxDistance = 0x100;  // float
        inline constexpr uintptr_t MinimizeDistance = 0x104;  // float
        inline constexpr uintptr_t TailVisible = 0x10d;  // bool
        inline constexpr uintptr_t TextColor3 = 0xe8;  // Color3
        inline constexpr uintptr_t TextSize = 0xc8;  // int64
        inline constexpr uintptr_t VerticalStudsOffset = 0x108;  // float
    }
    namespace BubbleChatMessageProperties {
        inline constexpr uintptr_t BackgroundColor3 = 0xf8;  // Color3
        inline constexpr uintptr_t BackgroundTransparency = 0xe0;  // double
        inline constexpr uintptr_t TailVisible = 0x110;  // bool
        inline constexpr uintptr_t TextColor3 = 0x104;  // Color3
        inline constexpr uintptr_t TextSize = 0xf0;  // int64
    }
    namespace CFramePose {
        inline constexpr uintptr_t CFrame = 0xb8;  // CoordinateFrame
    }
    namespace CanvasGroup {
        inline constexpr uintptr_t ResolutionScale = 0x9ac;  // float
    }
    namespace CapturesViewConfiguration {
        inline constexpr uintptr_t Open = 0x96;  // bool
    }
    namespace ChannelTabsConfiguration {
        inline constexpr uintptr_t BackgroundColor3 = 0xc0;  // Color3
        inline constexpr uintptr_t BackgroundTransparency = 0xa0;  // double
        inline constexpr uintptr_t Enabled = 0x10c;  // bool
        inline constexpr uintptr_t HoverBackgroundColor3 = 0xcc;  // Color3
        inline constexpr uintptr_t SelectedTabTextColor3 = 0xd8;  // Color3
        inline constexpr uintptr_t TextColor3 = 0xe4;  // Color3
        inline constexpr uintptr_t TextSize = 0xb0;  // int64
        inline constexpr uintptr_t TextStrokeColor3 = 0xf0;  // Color3
        inline constexpr uintptr_t TextStrokeTransparency = 0xb8;  // double
    }
    namespace CharacterMesh {
        inline constexpr uintptr_t BodyPart = 0x118;  // BodyPart
    }
    namespace ChatInputBarConfiguration {
        inline constexpr uintptr_t AutocompleteEnabled = 0x124;  // bool
        inline constexpr uintptr_t BackgroundColor3 = 0xe0;  // Color3
        inline constexpr uintptr_t BackgroundTransparency = 0xc0;  // double
        inline constexpr uintptr_t Enabled = 0x125;  // bool
        inline constexpr uintptr_t IsFocusedWrite = 0x126;  // bool
        inline constexpr uintptr_t KeyboardKeyCode = 0x120;  // KeyCode
        inline constexpr uintptr_t PlaceholderColor3 = 0xec;  // Color3
        inline constexpr uintptr_t TargetTextChannel = 0xa0;
        inline constexpr uintptr_t TextBox = 0xb0;
        inline constexpr uintptr_t TextColor3 = 0xf8;  // Color3
        inline constexpr uintptr_t TextSize = 0xd0;  // int64
        inline constexpr uintptr_t TextStrokeColor3 = 0x104;  // Color3
        inline constexpr uintptr_t TextStrokeTransparency = 0xd8;  // double
    }
    namespace ChatService {
        inline constexpr uintptr_t BubbleChatEnabled = 0x108;  // bool
        inline constexpr uintptr_t IsAutoMigrated = 0x109;  // bool
        inline constexpr uintptr_t LoadDefaultChat = 0x10a;  // bool
        inline constexpr uintptr_t ModerationMode = 0xa8;
    }
    namespace ChatWindowConfiguration {
        inline constexpr uintptr_t AbsolutePositionWrite = 0xe4;  // Vector2
        inline constexpr uintptr_t AbsoluteSizeWrite = 0xec;  // Vector2
        inline constexpr uintptr_t BackgroundColor3 = 0xc0;  // Color3
        inline constexpr uintptr_t BackgroundTransparency = 0xa0;  // double
        inline constexpr uintptr_t Enabled = 0x108;  // bool
        inline constexpr uintptr_t HeightScale = 0xf4;  // float
        inline constexpr uintptr_t HorizontalAlignment = 0xf8;  // Enums::HorizontalAlignmentEnum::HorizontalAlignment
        inline constexpr uintptr_t TextChannelDisplayMode = 0xfc;  // TextChannelDisplayMode
        inline constexpr uintptr_t TextColor3 = 0xcc;  // Color3
        inline constexpr uintptr_t TextSize = 0xb0;  // int64
        inline constexpr uintptr_t TextStrokeColor3 = 0xd8;  // Color3
        inline constexpr uintptr_t TextStrokeTransparency = 0xb8;  // double
        inline constexpr uintptr_t VerticalAlignment = 0x100;  // Enums::VerticalAlignmentEnum::VerticalAlignment
        inline constexpr uintptr_t WidthScale = 0x104;  // float
    }
    namespace ChatWindowMessageProperties {
        inline constexpr uintptr_t PrefixTextProperties = 0xe0;
        inline constexpr uintptr_t TextColor3 = 0x100;  // Color3
        inline constexpr uintptr_t TextSize = 0x118;  // int
        inline constexpr uintptr_t TextStrokeColor3 = 0x10c;  // Color3
        inline constexpr uintptr_t TextStrokeTransparency = 0xf8;  // double
    }
    namespace ClickDetector {
        inline constexpr uintptr_t MaxActivationDistance = 0xc8;  // float
    }
    namespace ClimbController {
        inline constexpr uintptr_t AccelerationTime = 0xc0;  // float
        inline constexpr uintptr_t BalanceMaxTorque = 0xc4;  // float
        inline constexpr uintptr_t BalanceSpeed = 0xc8;  // float
        inline constexpr uintptr_t MoveMaxForce = 0xcc;  // float
    }
    namespace Clothing {
        inline constexpr uintptr_t Color3 = 0xf8;  // Color3
    }
    namespace CloudClientService {
        inline constexpr uintptr_t RobloxRealityFilterEnabled = 0xba;  // bool
    }
    namespace Clouds {
        inline constexpr uintptr_t Cover = 0xa4;  // float
        inline constexpr uintptr_t Density = 0xa8;  // float
        inline constexpr uintptr_t Enabled = 0xac;  // bool
    }
    namespace Color3Value {
        inline constexpr uintptr_t Value = 0xa0;  // Color3
    }
    namespace ColorCorrectionEffect {
        inline constexpr uintptr_t Brightness = 0xa4;  // float
        inline constexpr uintptr_t Contrast = 0xa8;  // float
        inline constexpr uintptr_t Saturation = 0xac;  // float
        inline constexpr uintptr_t TintColor = 0x98;  // Color3
    }
    namespace ColorGradingEffect {
        inline constexpr uintptr_t TonemapperPreset = 0x98;  // TonemapperPreset
    }
    namespace CompositeValueCurve {
        inline constexpr uintptr_t CurveType = 0x98;  // CompositeValueCurveType
    }
    namespace ConeHandleAdornment {
        inline constexpr uintptr_t DoubleSided = 0x198;  // bool
        inline constexpr uintptr_t Height = 0x18c;  // float
        inline constexpr uintptr_t Hollow = 0x199;  // bool
        inline constexpr uintptr_t Radius = 0x190;  // float
        inline constexpr uintptr_t Shading = 0x194;  // Enums::AdornShading
    }
    namespace Constraints_AlignOrientation {
        inline constexpr uintptr_t AlignType = 0x188;
        inline constexpr uintptr_t LookAtPosition = 0x17c;  // Vector3
        inline constexpr uintptr_t MaxAngularVelocity = 0x18c;  // float
        inline constexpr uintptr_t MaxTorque = 0x190;  // float
        inline constexpr uintptr_t Mode = 0x194;
        inline constexpr uintptr_t PrimaryAxis = 0x158;  // Vector3
        inline constexpr uintptr_t PrimaryAxisOnly = 0x19c;  // bool
        inline constexpr uintptr_t ReactionTorqueEnabled = 0x19d;  // bool
        inline constexpr uintptr_t Responsiveness = 0x198;  // float
        inline constexpr uintptr_t RigidityEnabled = 0x19e;  // bool
        inline constexpr uintptr_t SecondaryAxis = 0x15c;  // Vector3
    }
    namespace Constraints_AlignPosition {
        inline constexpr uintptr_t ApplyAtCenterOfMass = 0x188;  // bool
        inline constexpr uintptr_t ForceLimitMode = 0x170;
        inline constexpr uintptr_t ForceRelativeTo = 0x174;
        inline constexpr uintptr_t MaxAxesForce = 0x158;  // Vector3
        inline constexpr uintptr_t MaxForce = 0x178;  // float
        inline constexpr uintptr_t MaxVelocity = 0x17c;  // float
        inline constexpr uintptr_t Mode = 0x180;
        inline constexpr uintptr_t Position = 0x164;  // Vector3
        inline constexpr uintptr_t ReactionForceEnabled = 0x189;  // bool
        inline constexpr uintptr_t Responsiveness = 0x184;  // float
        inline constexpr uintptr_t RigidityEnabled = 0x18a;  // bool
    }
    namespace Constraints_AngularVelocityActuator {
        inline constexpr uintptr_t AngularVelocity = 0x158;  // Vector3
        inline constexpr uintptr_t MaxTorque = 0x164;  // float
        inline constexpr uintptr_t ReactionTorqueEnabled = 0x16c;  // bool
        inline constexpr uintptr_t RelativeTo = 0x168;
    }
    namespace Constraints_AnimationConstraint {
        inline constexpr uintptr_t AngularDamping = 0x158;  // float
        inline constexpr uintptr_t AngularStrength = 0x15c;  // float
        inline constexpr uintptr_t EnableSkinning = 0x170;  // bool
        inline constexpr uintptr_t IsKinematic = 0x171;  // bool
        inline constexpr uintptr_t LinearDamping = 0x160;  // float
        inline constexpr uintptr_t LinearStrength = 0x164;  // float
        inline constexpr uintptr_t MaxForce = 0x168;  // float
        inline constexpr uintptr_t MaxTorque = 0x16c;  // float
    }
    namespace Constraints_BallSocketConstraint {
        inline constexpr uintptr_t EnableSkinning = 0x170;  // bool
        inline constexpr uintptr_t LimitsEnabled = 0x171;  // bool
        inline constexpr uintptr_t Radius = 0x15c;  // float
        inline constexpr uintptr_t Restitution = 0x160;  // float
        inline constexpr uintptr_t TwistLimitsEnabled = 0x172;  // bool
        inline constexpr uintptr_t TwistLowerAngle = 0x164;  // float
        inline constexpr uintptr_t TwistUpperAngle = 0x168;  // float
        inline constexpr uintptr_t UpperAngle = 0x16c;  // float
    }
    namespace Constraints_Constraint {
        inline constexpr uintptr_t Color = 0xd8;  // BrickColor
        inline constexpr uintptr_t Enabled = 0xa1;  // bool
        inline constexpr uintptr_t Visible = 0xdc;  // bool
    }
    namespace Constraints_CylindricalConstraint {
        inline constexpr uintptr_t AngularActuatorType = 0x1b8;
        inline constexpr uintptr_t AngularLimitsEnabled = 0x1e8;  // bool
        inline constexpr uintptr_t AngularResponsiveness = 0x1bc;  // float
        inline constexpr uintptr_t AngularRestitution = 0x1c0;  // float
        inline constexpr uintptr_t AngularSpeed = 0x1c4;  // float
        inline constexpr uintptr_t AngularVelocity = 0x1c8;  // float
        inline constexpr uintptr_t InclinationAngle = 0x1cc;  // float
        inline constexpr uintptr_t LowerAngle = 0x1d0;  // float
        inline constexpr uintptr_t MotorMaxAngularAcceleration = 0x1d4;  // float
        inline constexpr uintptr_t MotorMaxTorque = 0x1d8;  // float
        inline constexpr uintptr_t RotationAxisVisible = 0x1e9;  // bool
        inline constexpr uintptr_t ServoMaxTorque = 0x1dc;  // float
        inline constexpr uintptr_t SoftlockAngularServoUponReachingTarget = 0x1ea;  // bool
        inline constexpr uintptr_t TargetAngle = 0x1e0;  // float
        inline constexpr uintptr_t UpperAngle = 0x1e4;  // float
    }
    namespace Constraints_HingeConstraint {
        inline constexpr uintptr_t ActuatorType = 0x158;
        inline constexpr uintptr_t AngularResponsiveness = 0x15c;  // float
        inline constexpr uintptr_t AngularSpeed = 0x160;  // float
        inline constexpr uintptr_t AngularVelocity = 0x164;  // float
        inline constexpr uintptr_t LimitsEnabled = 0x188;  // bool
        inline constexpr uintptr_t LowerAngle = 0x168;  // float
        inline constexpr uintptr_t MotorMaxAcceleration = 0x16c;  // float
        inline constexpr uintptr_t MotorMaxTorque = 0x170;  // float
        inline constexpr uintptr_t Radius = 0x174;  // float
        inline constexpr uintptr_t Restitution = 0x178;  // float
        inline constexpr uintptr_t ServoMaxTorque = 0x17c;  // float
        inline constexpr uintptr_t SoftlockServoUponReachingTarget = 0x189;  // bool
        inline constexpr uintptr_t TargetAngle = 0x180;  // float
        inline constexpr uintptr_t UpperAngle = 0x184;  // float
    }
    namespace Constraints_LineForce {
        inline constexpr uintptr_t ApplyAtCenterOfMass = 0x160;  // bool
        inline constexpr uintptr_t InverseSquareLaw = 0x161;  // bool
        inline constexpr uintptr_t Magnitude = 0x158;  // float
        inline constexpr uintptr_t MaxForce = 0x15c;  // float
        inline constexpr uintptr_t ReactionForceEnabled = 0x162;  // bool
    }
    namespace Constraints_LinearVelocity {
        inline constexpr uintptr_t ForceLimitMode = 0x14;  // at *(object + 0x160) + this
        inline constexpr uintptr_t ForceLimitsEnabled = 0x9;  // bool; at *(object + 0x160) + this
        inline constexpr uintptr_t LineDirection = 0x180;  // Vector3
        inline constexpr uintptr_t MaxAxesForce = 0x220;  // Vector3
        inline constexpr uintptr_t MaxForce = 0x10;  // float; at *(object + 0x160) + this
        inline constexpr uintptr_t MaxPlanarAxesForce = 0x1b0;  // Vector2
        inline constexpr uintptr_t PlaneVelocity = 0x118;  // Vector2; at *(object + 0x200) + this
        inline constexpr uintptr_t PrimaryTangentAxis = 0x1e8;  // Vector3
        inline constexpr uintptr_t ReactionForceEnabled = 0x15c;  // bool
        inline constexpr uintptr_t RelativeTo = 0xc;  // at *(object + 0x160) + this
        inline constexpr uintptr_t SecondaryTangentAxis = 0x1f4;  // Vector3
        inline constexpr uintptr_t VectorVelocity = 0x22c;  // Vector3
        inline constexpr uintptr_t VelocityConstraintMode = 0x158;
    }
    namespace Constraints_NoCollisionConstraint {
        inline constexpr uintptr_t Enabled = 0xc0;  // bool
    }
    namespace Constraints_RigidConstraint {
        inline constexpr uintptr_t EnableSkinning = 0x150;  // bool
    }
    namespace Constraints_RodConstraint {
        inline constexpr uintptr_t Length = 0x158;  // float
        inline constexpr uintptr_t LimitAngle0 = 0x15c;  // float
        inline constexpr uintptr_t LimitAngle1 = 0x160;  // float
        inline constexpr uintptr_t LimitsEnabled = 0x168;  // bool
        inline constexpr uintptr_t Thickness = 0x164;  // float
    }
    namespace Constraints_RopeConstraint {
        inline constexpr uintptr_t Length = 0x158;  // float
        inline constexpr uintptr_t Restitution = 0x15c;  // float
        inline constexpr uintptr_t Thickness = 0x160;  // float
        inline constexpr uintptr_t WinchEnabled = 0x174;  // bool
        inline constexpr uintptr_t WinchForce = 0x164;  // float
        inline constexpr uintptr_t WinchResponsiveness = 0x168;  // float
        inline constexpr uintptr_t WinchSpeed = 0x16c;  // float
        inline constexpr uintptr_t WinchTarget = 0x170;  // float
    }
    namespace Constraints_SlidingBallConstraint {
        inline constexpr uintptr_t ActuatorType = 0x158;
        inline constexpr uintptr_t LimitsEnabled = 0x188;  // bool
        inline constexpr uintptr_t LinearResponsiveness = 0x15c;  // float
        inline constexpr uintptr_t LowerLimit = 0x160;  // float
        inline constexpr uintptr_t MotorMaxAcceleration = 0x164;  // float
        inline constexpr uintptr_t MotorMaxForce = 0x168;  // float
        inline constexpr uintptr_t Restitution = 0x16c;  // float
        inline constexpr uintptr_t ServoMaxForce = 0x170;  // float
        inline constexpr uintptr_t Size = 0x174;  // float
        inline constexpr uintptr_t SoftlockServoUponReachingTarget = 0x189;  // bool
        inline constexpr uintptr_t Speed = 0x178;  // float
        inline constexpr uintptr_t TargetPosition = 0x17c;  // float
        inline constexpr uintptr_t UpperLimit = 0x180;  // float
        inline constexpr uintptr_t Velocity = 0x184;  // float
    }
    namespace Constraints_SpringConstraint {
        inline constexpr uintptr_t Coils = 0x158;  // float
        inline constexpr uintptr_t Damping = 0x15c;  // float
        inline constexpr uintptr_t FreeLength = 0x160;  // float
        inline constexpr uintptr_t LimitsEnabled = 0x17c;  // bool
        inline constexpr uintptr_t MaxForce = 0x164;  // float
        inline constexpr uintptr_t MaxLength = 0x168;  // float
        inline constexpr uintptr_t MinLength = 0x16c;  // float
        inline constexpr uintptr_t Radius = 0x170;  // float
        inline constexpr uintptr_t Stiffness = 0x174;  // float
        inline constexpr uintptr_t Thickness = 0x178;  // float
    }
    namespace Constraints_Torque {
        inline constexpr uintptr_t RelativeTo = 0x164;
    }
    namespace Constraints_TorsionSpringConstraint {
        inline constexpr uintptr_t Coils = 0x158;  // float
        inline constexpr uintptr_t Damping = 0x15c;  // float
        inline constexpr uintptr_t LimitEnabled = 0x174;  // bool
        inline constexpr uintptr_t LimitsEnabled = 0x174;  // bool
        inline constexpr uintptr_t MaxAngle = 0x160;  // float
        inline constexpr uintptr_t MaxTorque = 0x164;  // float
        inline constexpr uintptr_t Radius = 0x168;  // float
        inline constexpr uintptr_t Restitution = 0x16c;  // float
        inline constexpr uintptr_t Stiffness = 0x170;  // float
    }
    namespace Constraints_UniversalConstraint {
        inline constexpr uintptr_t LimitsEnabled = 0x164;  // bool
        inline constexpr uintptr_t MaxAngle = 0x158;  // float
        inline constexpr uintptr_t Radius = 0x15c;  // float
        inline constexpr uintptr_t Restitution = 0x160;  // float
    }
    namespace Constraints_VectorForce {
        inline constexpr uintptr_t ApplyAtCenterOfMass = 0x168;  // bool
        inline constexpr uintptr_t Force = 0x158;  // Vector3
        inline constexpr uintptr_t RelativeTo = 0x164;
    }
    namespace Constraints_WeldConstraint {
        inline constexpr uintptr_t Enabled = 0xc0;  // bool
    }
    namespace ControlState {
        inline constexpr uintptr_t StateSchema = 0x98;  // BinaryString
    }
    namespace ControllerBase {
        inline constexpr uintptr_t BalanceRigidityEnabled = 0xa5;  // bool
        inline constexpr uintptr_t MoveSpeedFactor = 0xa0;  // float
    }
    namespace ControllerManager {
        inline constexpr uintptr_t ActiveController = 0x8;
        inline constexpr uintptr_t BaseMoveSpeed = 0x6c;  // float
        inline constexpr uintptr_t BaseTurnSpeed = 0x70;  // float
        inline constexpr uintptr_t ClimbSensor = 0x18;
        inline constexpr uintptr_t FacingDirection = 0x48;  // Vector3
        inline constexpr uintptr_t GroundSensor = 0x28;
        inline constexpr uintptr_t MovingDirection = 0x54;  // Vector3
        inline constexpr uintptr_t RootPart = 0x38;
        inline constexpr uintptr_t UpDirection = 0x60;  // Vector3
    }
    namespace ControllerPartSensor {
        inline constexpr uintptr_t LadderSearchHeight = 0x27c;  // float
        inline constexpr uintptr_t LadderSearchOffset = 0x280;  // float
        inline constexpr uintptr_t SearchDistance = 0x284;  // float
        inline constexpr uintptr_t SensorMode = 0x28c;  // SensorMode
    }
    namespace CoreGuiConfiguration {
        inline constexpr uintptr_t CapturesViewConfiguration = 0xa8;
        inline constexpr uintptr_t PlayerListConfiguration = 0xb8;
        inline constexpr uintptr_t SelfViewConfiguration = 0xc8;
    }
    namespace CustomEvent {
        inline constexpr uintptr_t PersistedCurrentValue = 0x98;  // float
    }
    namespace CustomParticleEmitter {
        inline constexpr uintptr_t Acceleration = 0x1c0;  // Vector3
        inline constexpr uintptr_t Brightness = 0x1fc;  // float
        inline constexpr uintptr_t Color = 0x160;  // ColorSequence
        inline constexpr uintptr_t Drag = 0x200;  // float
        inline constexpr uintptr_t EmissionDirection = 0x204;  // NormalId
        inline constexpr uintptr_t Enabled = 0x248;  // bool
        inline constexpr uintptr_t FlipbookBlendFrames = 0x249;  // bool
        inline constexpr uintptr_t FlipbookFramerate = 0x1cc;  // NumberRange
        inline constexpr uintptr_t FlipbookLayout = 0x208;  // ParticleFlipbookLayout
        inline constexpr uintptr_t FlipbookMode = 0x20c;  // ParticleFlipbookMode
        inline constexpr uintptr_t FlipbookSizeX = 0x210;  // int
        inline constexpr uintptr_t FlipbookSizeY = 0x214;  // int
        inline constexpr uintptr_t FlipbookStartRandom = 0x24a;  // bool
        inline constexpr uintptr_t Lifetime = 0x1d4;  // NumberRange
        inline constexpr uintptr_t LightEmission = 0x218;  // float
        inline constexpr uintptr_t LightInfluence = 0x21c;  // float
        inline constexpr uintptr_t LocalTransparencyModifier = 0x220;  // float
        inline constexpr uintptr_t LockedToPart = 0x24b;  // bool
        inline constexpr uintptr_t Orientation = 0x224;  // ParticleOrientation
        inline constexpr uintptr_t Rate = 0x228;  // float
        inline constexpr uintptr_t RotSpeed = 0x1dc;  // NumberRange
        inline constexpr uintptr_t Rotation = 0x1e4;  // NumberRange
        inline constexpr uintptr_t Shape = 0x22c;  // ParticleEmitterShape
        inline constexpr uintptr_t ShapeInOut = 0x230;  // ParticleEmitterShapeInOut
        inline constexpr uintptr_t ShapePartial = 0x234;  // float
        inline constexpr uintptr_t ShapeStyle = 0x238;  // ParticleEmitterShapeStyle
        inline constexpr uintptr_t Size = 0xa0;  // NumberSequence
        inline constexpr uintptr_t Speed = 0x1ec;  // NumberRange
        inline constexpr uintptr_t SpreadAngle = 0x1f4;  // Vector2
        inline constexpr uintptr_t Squash = 0xe0;  // NumberSequence
        inline constexpr uintptr_t TimeScale = 0x23c;  // float
        inline constexpr uintptr_t Transparency = 0x120;  // NumberSequence
        inline constexpr uintptr_t VelocityInheritance = 0x240;  // float
        inline constexpr uintptr_t VelocitySpread = 0x1f4;  // float
        inline constexpr uintptr_t WindAffectsDrag = 0x24c;  // bool
        inline constexpr uintptr_t ZOffset = 0x244;  // float
    }
    namespace CylinderHandleAdornment {
        inline constexpr uintptr_t Angle = 0x18c;  // float
        inline constexpr uintptr_t DoubleSided = 0x1a0;  // bool
        inline constexpr uintptr_t Height = 0x190;  // float
        inline constexpr uintptr_t InnerRadius = 0x194;  // float
        inline constexpr uintptr_t Radius = 0x198;  // float
        inline constexpr uintptr_t Shading = 0x19c;  // Enums::AdornShading
    }
    namespace DataModel {
        inline constexpr uintptr_t ForceR15 = 0xa8;  // bool
    }
    namespace DataModelMesh {
        inline constexpr uintptr_t Offset = 0xa0;  // Vector3
        inline constexpr uintptr_t Scale = 0xac;  // Vector3
        inline constexpr uintptr_t VertexColor = 0xb8;  // Vector3
    }
    namespace DataStoreGetOptions {
        inline constexpr uintptr_t UseCache = 0x95;  // bool
    }
    namespace DataStoreOptions {
        inline constexpr uintptr_t AllScopes = 0x95;  // bool
    }
    namespace DataStoreService {
        inline constexpr uintptr_t AutomaticRetry = 0xb0;  // bool
        inline constexpr uintptr_t LegacyNamingScheme = 0xb1;  // bool
    }
    namespace DebrisService {
        inline constexpr uintptr_t MaxItems = 0xb0;  // int
    }
    namespace Decal {
        inline constexpr uintptr_t AutoLocalize = 0x240;  // bool
        inline constexpr uintptr_t Color3 = 0x1f8;  // Color3
        inline constexpr uintptr_t EmissiveMaskContent = 0xc8;  // Content
        inline constexpr uintptr_t EmissiveStrength = 0x220;  // float
        inline constexpr uintptr_t EmissiveTint = 0x204;  // Color3
        inline constexpr uintptr_t LocalTransparencyModifier = 0x224;  // float
        inline constexpr uintptr_t MetalnessMapContent = 0x118;  // Content
        inline constexpr uintptr_t NormalMapContent = 0x140;  // Content
        inline constexpr uintptr_t ResampleMode = 0x228;  // Enums::ImageResampleMode
        inline constexpr uintptr_t Rotation = 0x22c;  // float
        inline constexpr uintptr_t RoughnessMapContent = 0x168;  // Content
        inline constexpr uintptr_t Shiny = 0x230;  // float
        inline constexpr uintptr_t Specular = 0x234;  // float
        inline constexpr uintptr_t TextureContent = 0x190;  // Content
        inline constexpr uintptr_t TexturePackContent = 0x1b8;  // Content
        inline constexpr uintptr_t TexturePackMetadata = 0x1e0;
        inline constexpr uintptr_t Transparency = 0x238;  // float
        inline constexpr uintptr_t UVOffset = 0x210;  // Vector2
        inline constexpr uintptr_t UVScale = 0x218;  // Vector2
        inline constexpr uintptr_t ZIndex = 0x23c;  // int
    }
    namespace DeferredAssetManagerService {
        inline constexpr uintptr_t JoiningPlaceId = 0xb0;  // int64
        inline constexpr uintptr_t JoiningUniverseId = 0xb8;  // int64
        inline constexpr uintptr_t PregameLoadingScreenOnly = 0xc0;  // bool
    }
    namespace DepthOfFieldEffect {
        inline constexpr uintptr_t FarIntensity = 0x98;  // float
        inline constexpr uintptr_t FocusDistance = 0x9c;  // float
        inline constexpr uintptr_t InFocusRadius = 0xa0;  // float
        inline constexpr uintptr_t NearIntensity = 0xa4;  // float
    }
    namespace DialogChoice {
        inline constexpr uintptr_t GoodbyeChoiceActive = 0xe8;  // bool
        inline constexpr uintptr_t GoodbyeDialog = 0xa0;
        inline constexpr uintptr_t ResponseDialog = 0xb8;
        inline constexpr uintptr_t UserDialog = 0xd0;
    }
    namespace DialogRoot {
        inline constexpr uintptr_t BehaviorType = 0xd4;  // Enums::DialogBehaviorTypeEnum::DialogBehaviorType
        inline constexpr uintptr_t ConversationDistance = 0xd8;  // float
        inline constexpr uintptr_t GoodbyeChoiceActive = 0xe8;  // bool
        inline constexpr uintptr_t GoodbyeDialog = 0x98;
        inline constexpr uintptr_t InUse = 0xe9;  // bool
        inline constexpr uintptr_t InitialPrompt = 0xb0;
        inline constexpr uintptr_t Purpose = 0xdc;  // Enums::DialogPurposeEnum::DialogPurpose
        inline constexpr uintptr_t Tone = 0xe0;  // Enums::DialogToneEnum::DialogTone
        inline constexpr uintptr_t TriggerDistance = 0xe4;  // float
        inline constexpr uintptr_t TriggerOffset = 0xc8;  // Vector3
    }
    namespace DigitsRigDescription {
        inline constexpr uintptr_t Index1 = 0x98;
        inline constexpr uintptr_t Index1TposeAdjustment = 0x188;  // CoordinateFrame
        inline constexpr uintptr_t Index2 = 0xa8;
        inline constexpr uintptr_t Index2TposeAdjustment = 0x1b8;  // CoordinateFrame
        inline constexpr uintptr_t Index3 = 0xb8;
        inline constexpr uintptr_t Index3TposeAdjustment = 0x1e8;  // CoordinateFrame
        inline constexpr uintptr_t IndexRange = 0x458;  // Vector3
        inline constexpr uintptr_t IndexSize = 0x494;  // float
        inline constexpr uintptr_t Middle1 = 0xc8;
        inline constexpr uintptr_t Middle1TposeAdjustment = 0x218;  // CoordinateFrame
        inline constexpr uintptr_t Middle2 = 0xd8;
        inline constexpr uintptr_t Middle2TposeAdjustment = 0x248;  // CoordinateFrame
        inline constexpr uintptr_t Middle3 = 0xe8;
        inline constexpr uintptr_t Middle3TposeAdjustment = 0x278;  // CoordinateFrame
        inline constexpr uintptr_t MiddleRange = 0x464;  // Vector3
        inline constexpr uintptr_t MiddleSize = 0x498;  // float
        inline constexpr uintptr_t Pinky1 = 0xf8;
        inline constexpr uintptr_t Pinky1TposeAdjustment = 0x2a8;  // CoordinateFrame
        inline constexpr uintptr_t Pinky2 = 0x108;
        inline constexpr uintptr_t Pinky2TposeAdjustment = 0x2d8;  // CoordinateFrame
        inline constexpr uintptr_t Pinky3 = 0x118;
        inline constexpr uintptr_t Pinky3TposeAdjustment = 0x308;  // CoordinateFrame
        inline constexpr uintptr_t PinkyRange = 0x470;  // Vector3
        inline constexpr uintptr_t PinkySize = 0x49c;  // float
        inline constexpr uintptr_t Ring1 = 0x128;
        inline constexpr uintptr_t Ring1TposeAdjustment = 0x338;  // CoordinateFrame
        inline constexpr uintptr_t Ring2 = 0x138;
        inline constexpr uintptr_t Ring2TposeAdjustment = 0x368;  // CoordinateFrame
        inline constexpr uintptr_t Ring3 = 0x148;
        inline constexpr uintptr_t Ring3TposeAdjustment = 0x398;  // CoordinateFrame
        inline constexpr uintptr_t RingRange = 0x47c;  // Vector3
        inline constexpr uintptr_t RingSize = 0x4a0;  // float
        inline constexpr uintptr_t Side = 0x4a4;  // Enums::DigitsSide
        inline constexpr uintptr_t Thumb1 = 0x158;
        inline constexpr uintptr_t Thumb1TposeAdjustment = 0x3c8;  // CoordinateFrame
        inline constexpr uintptr_t Thumb2 = 0x168;
        inline constexpr uintptr_t Thumb2TposeAdjustment = 0x3f8;  // CoordinateFrame
        inline constexpr uintptr_t Thumb3 = 0x178;
        inline constexpr uintptr_t Thumb3TposeAdjustment = 0x428;  // CoordinateFrame
        inline constexpr uintptr_t ThumbRange = 0x488;  // Vector3
        inline constexpr uintptr_t ThumbSize = 0x4a8;  // float
    }
    namespace DoubleConstrainedValue {
        inline constexpr uintptr_t MaxValue = 0xa0;  // double
        inline constexpr uintptr_t MinValue = 0xa8;  // double
    }
    namespace DoublePose {
        inline constexpr uintptr_t Value = 0xb8;  // double
    }
    namespace DoubleValue {
        inline constexpr uintptr_t Value = 0xa0;  // double
    }
    namespace DragDetector {
        inline constexpr uintptr_t ApplyAtCenterOfMass = 0x288;  // bool
        inline constexpr uintptr_t Axis = 0x218;  // Vector3
        inline constexpr uintptr_t DragFrame = 0x1b8;  // CoordinateFrame
        inline constexpr uintptr_t DragStyle = 0x254;  // DragDetectorDragStyle
        inline constexpr uintptr_t Enabled = 0x289;  // bool
        inline constexpr uintptr_t GamepadModeSwitchKeyCode = 0x258;  // KeyCode
        inline constexpr uintptr_t KeyboardModeSwitchKeyCode = 0x25c;  // KeyCode
        inline constexpr uintptr_t MaxDragAngle = 0x260;  // float
        inline constexpr uintptr_t MaxDragTranslation = 0x224;  // Vector3
        inline constexpr uintptr_t MaxForce = 0x264;  // float
        inline constexpr uintptr_t MaxTorque = 0x268;  // float
        inline constexpr uintptr_t MinDragAngle = 0x26c;  // float
        inline constexpr uintptr_t MinDragTranslation = 0x230;  // Vector3
        inline constexpr uintptr_t PermissionPolicy = 0x270;  // DragDetectorPermissionPolicy
        inline constexpr uintptr_t PhysicalDragHitPoint = 0x23c;  // Vector3
        inline constexpr uintptr_t PhysicalDragIsInVR = 0x28a;  // bool
        inline constexpr uintptr_t PhysicalDragTargetFrame = 0x1e8;  // CoordinateFrame
        inline constexpr uintptr_t ResponseStyle = 0x274;  // DragDetectorResponseStyle
        inline constexpr uintptr_t Responsiveness = 0x278;  // float
        inline constexpr uintptr_t RunLocally = 0x28b;  // bool
        inline constexpr uintptr_t SecondaryAxis = 0x248;  // Vector3
        inline constexpr uintptr_t TrackballRadialPullFactor = 0x27c;  // float
        inline constexpr uintptr_t TrackballRollFactor = 0x280;  // float
        inline constexpr uintptr_t VRSwitchKeyCode = 0x284;  // KeyCode
    }
    namespace EditableImage {
        inline constexpr uintptr_t IsReplicatedCopy = 0xc0;  // bool
    }
    namespace EditableMesh {
        inline constexpr uintptr_t IsReplicatedCopy = 0xc1;  // bool
    }
    namespace EditableService {
        inline constexpr uintptr_t EditableStatus = 0xb0;  // Enums::EditableStatusEnum::EditableStatus
    }
    namespace EulerRotationCurve {
        inline constexpr uintptr_t RotationOrder = 0x98;  // EulerAngles::RotationOrder
    }
    namespace ExperienceInviteOptions {
        inline constexpr uintptr_t InviteMessageId = 0x98;
        inline constexpr uintptr_t InviteUser = 0xe0;  // int64
        inline constexpr uintptr_t LaunchData = 0xb0;
        inline constexpr uintptr_t PromptMessage = 0xc8;
    }
    namespace ExperienceStateCapture_ExperienceStateRecordingService {
        inline constexpr uintptr_t IsServerDataModelRecorderActive = 0xb0;  // bool
    }
    namespace ExperienceStateCaptureService {
        inline constexpr uintptr_t HiddenSelectionEnabled = 0xa8;  // bool
        inline constexpr uintptr_t SelectionMode = 0xa4;  // Enums::ExperienceStateCaptureSelectionMode
    }
    namespace Explosion {
        inline constexpr uintptr_t BlastPressure = 0xa4;  // float
        inline constexpr uintptr_t BlastRadius = 0xa8;  // float
        inline constexpr uintptr_t DestroyJointRadiusPercent = 0xac;  // float
        inline constexpr uintptr_t ExplosionType = 0xb0;  // Enums::ExplosionTypeEnum::ExplosionType
        inline constexpr uintptr_t LocalTransparencyModifier = 0xb4;  // float
        inline constexpr uintptr_t TimeScale = 0xb8;  // float
        inline constexpr uintptr_t Visible = 0xbc;  // bool
    }
    namespace FaceControls {
        inline constexpr uintptr_t ChinRaiser = 0xc0;  // float
        inline constexpr uintptr_t ChinRaiserUpperLip = 0xc4;  // float
        inline constexpr uintptr_t Corrugator = 0xc8;  // float
        inline constexpr uintptr_t EyesLookDown = 0xcc;  // float
        inline constexpr uintptr_t EyesLookLeft = 0xd0;  // float
        inline constexpr uintptr_t EyesLookRight = 0xd4;  // float
        inline constexpr uintptr_t EyesLookUp = 0xd8;  // float
        inline constexpr uintptr_t FlatPucker = 0xdc;  // float
        inline constexpr uintptr_t Funneler = 0xe0;  // float
        inline constexpr uintptr_t InternalOverrideFACSData = 0xa0;  // BinaryString
        inline constexpr uintptr_t JawDrop = 0xe4;  // float
        inline constexpr uintptr_t JawLeft = 0xe8;  // float
        inline constexpr uintptr_t JawRight = 0xec;  // float
        inline constexpr uintptr_t LeftBrowLowerer = 0xf0;  // float
        inline constexpr uintptr_t LeftCheekPuff = 0xf4;  // float
        inline constexpr uintptr_t LeftCheekRaiser = 0xf8;  // float
        inline constexpr uintptr_t LeftDimpler = 0xfc;  // float
        inline constexpr uintptr_t LeftEyeClosed = 0x100;  // float
        inline constexpr uintptr_t LeftEyeUpperLidRaiser = 0x104;  // float
        inline constexpr uintptr_t LeftInnerBrowRaiser = 0x108;  // float
        inline constexpr uintptr_t LeftLipCornerDown = 0x10c;  // float
        inline constexpr uintptr_t LeftLipCornerPuller = 0x110;  // float
        inline constexpr uintptr_t LeftLipStretcher = 0x114;  // float
        inline constexpr uintptr_t LeftLowerLipDepressor = 0x118;  // float
        inline constexpr uintptr_t LeftNoseWrinkler = 0x11c;  // float
        inline constexpr uintptr_t LeftOuterBrowRaiser = 0x120;  // float
        inline constexpr uintptr_t LeftUpperLipRaiser = 0x124;  // float
        inline constexpr uintptr_t LipPresser = 0x128;  // float
        inline constexpr uintptr_t LipsTogether = 0x12c;  // float
        inline constexpr uintptr_t LowerLipSuck = 0x130;  // float
        inline constexpr uintptr_t MouthLeft = 0x134;  // float
        inline constexpr uintptr_t MouthRight = 0x138;  // float
        inline constexpr uintptr_t Pucker = 0x13c;  // float
        inline constexpr uintptr_t RightBrowLowerer = 0x140;  // float
        inline constexpr uintptr_t RightCheekPuff = 0x144;  // float
        inline constexpr uintptr_t RightCheekRaiser = 0x148;  // float
        inline constexpr uintptr_t RightDimpler = 0x14c;  // float
        inline constexpr uintptr_t RightEyeClosed = 0x150;  // float
        inline constexpr uintptr_t RightEyeUpperLidRaiser = 0x154;  // float
        inline constexpr uintptr_t RightInnerBrowRaiser = 0x158;  // float
        inline constexpr uintptr_t RightLipCornerDown = 0x15c;  // float
        inline constexpr uintptr_t RightLipCornerPuller = 0x160;  // float
        inline constexpr uintptr_t RightLipStretcher = 0x164;  // float
        inline constexpr uintptr_t RightLowerLipDepressor = 0x168;  // float
        inline constexpr uintptr_t RightNoseWrinkler = 0x16c;  // float
        inline constexpr uintptr_t RightOuterBrowRaiser = 0x170;  // float
        inline constexpr uintptr_t RightUpperLipRaiser = 0x174;  // float
        inline constexpr uintptr_t TongueDown = 0x178;  // float
        inline constexpr uintptr_t TongueOut = 0x17c;  // float
        inline constexpr uintptr_t TongueUp = 0x180;  // float
        inline constexpr uintptr_t UpperLipSuck = 0x184;  // float
    }
    namespace FaceInstance {
        inline constexpr uintptr_t Face = 0x98;  // NormalId
    }
    namespace FacialAnimationStreamingServiceV2 {
        inline constexpr uintptr_t ServiceState = 0xf0;  // int
    }
    namespace Feature {
        inline constexpr uintptr_t FaceId = 0x98;  // NormalId
        inline constexpr uintptr_t InOut = 0x9c;  // Enums::InOutEnum::InOut
        inline constexpr uintptr_t LeftRight = 0xa0;  // Enums::LeftRightEnum::LeftRight
        inline constexpr uintptr_t TopBottom = 0xa4;  // Enums::TopBottomEnum::TopBottom
    }
    namespace FeatureMatchingTable {
        inline constexpr uintptr_t Data = 0xb8;  // SharedString
    }
    namespace FileSyncItem {
        inline constexpr uintptr_t AutoSync = 0xc0;  // bool
        inline constexpr uintptr_t Enabled = 0xc1;  // bool
        inline constexpr uintptr_t Target = 0xb0;
    }
    namespace Fire {
        inline constexpr uintptr_t Color = 0xa0;  // Color3
        inline constexpr uintptr_t Enabled = 0xc8;  // bool
        inline constexpr uintptr_t Heat = 0xc0;  // float
        inline constexpr uintptr_t LocalTransparencyModifier = 0xb8;  // float
        inline constexpr uintptr_t SecondaryColor = 0xac;  // Color3
        inline constexpr uintptr_t Size = 0xc4;  // float
        inline constexpr uintptr_t TimeScale = 0xbc;  // float
        inline constexpr uintptr_t heat_xml = 0xc0;  // float
        inline constexpr uintptr_t size = 0xc4;  // float
        inline constexpr uintptr_t size_xml = 0xc4;  // float
    }
    namespace Flag {
        inline constexpr uintptr_t TeamColor = 0x530;  // BrickColor
    }
    namespace FlagStand {
        inline constexpr uintptr_t TeamColor = 0x1b8;  // BrickColor
    }
    namespace FloorWire {
        inline constexpr uintptr_t CycleOffset = 0x128;  // float
        inline constexpr uintptr_t StudsBetweenTextures = 0x12c;  // float
        inline constexpr uintptr_t TextureSize = 0x120;  // Vector2
        inline constexpr uintptr_t Velocity = 0x130;  // float
        inline constexpr uintptr_t WireRadius = 0x134;  // float
    }
    namespace ForceField {
        inline constexpr uintptr_t Visible = 0xa0;  // bool
    }
    namespace FormFactorPart {
        inline constexpr uintptr_t FormFactor = 0x1a8;  // Enums::FormFactorEnum::FormFactor
        inline constexpr uintptr_t formFactor = 0x1a8;  // Enums::FormFactorEnum::FormFactor
        inline constexpr uintptr_t formFactorRaw = 0x1a8;  // Enums::FormFactorEnum::FormFactor
    }
    namespace FunctionalTest {
        inline constexpr uintptr_t AllowSleep = 0xb8;  // bool
        inline constexpr uintptr_t Description = 0x98;
        inline constexpr uintptr_t HasMigratedSettingsToTestService = 0xb9;  // bool
        inline constexpr uintptr_t Is30FpsThrottleEnabled = 0xba;  // bool
        inline constexpr uintptr_t PhysicsEnvironmentalThrottle = 0xbb;  // bool
        inline constexpr uintptr_t Timeout = 0xb0;  // double
    }
    namespace GamepadService {
        inline constexpr uintptr_t GamepadCursorEnabled = 0xb0;  // bool
    }
    namespace Glue {
        inline constexpr uintptr_t F0 = 0x170;  // Vector3
        inline constexpr uintptr_t F1 = 0x17c;  // Vector3
        inline constexpr uintptr_t F2 = 0x188;  // Vector3
        inline constexpr uintptr_t F3 = 0x194;  // Vector3
    }
    namespace GroundController {
        inline constexpr uintptr_t AccelerationLean = 0xc0;  // float
        inline constexpr uintptr_t AccelerationTime = 0xc4;  // float
        inline constexpr uintptr_t BalanceMaxTorque = 0xc8;  // float
        inline constexpr uintptr_t BalanceSpeed = 0xcc;  // float
        inline constexpr uintptr_t DecelerationTime = 0xd0;  // float
        inline constexpr uintptr_t Friction = 0xd4;  // float
        inline constexpr uintptr_t FrictionWeight = 0xd8;  // float
        inline constexpr uintptr_t GroundOffset = 0xdc;  // float
        inline constexpr uintptr_t StandForce = 0xe0;  // float
        inline constexpr uintptr_t StandSpeed = 0xe4;  // float
        inline constexpr uintptr_t TurnSpeedFactor = 0xe8;  // float
    }
    namespace GuiBase2d {
        inline constexpr uintptr_t SelectionBehaviorDown = 0x108;  // Enums::SelectionBehavior
        inline constexpr uintptr_t SelectionBehaviorLeft = 0x10c;  // Enums::SelectionBehavior
        inline constexpr uintptr_t SelectionBehaviorRight = 0x110;  // Enums::SelectionBehavior
        inline constexpr uintptr_t SelectionBehaviorUp = 0x114;  // Enums::SelectionBehavior
    }
    namespace GuiBase3d {
        inline constexpr uintptr_t Color = 0xc0;  // BrickColor
        inline constexpr uintptr_t Color3 = 0xc0;  // Color3
        inline constexpr uintptr_t Transparency = 0xcc;  // float
        inline constexpr uintptr_t Visible = 0xd0;  // bool
    }
    namespace GuiButton {
        inline constexpr uintptr_t AutoButtonColor = 0x9ec;  // bool
        inline constexpr uintptr_t MouseButton1ClickConnectionCount = 0x9d0;  // int
        inline constexpr uintptr_t MouseButton1DownConnectionCount = 0x9d4;  // int
        inline constexpr uintptr_t MouseButton1UpConnectionCount = 0x9d8;  // int
        inline constexpr uintptr_t MouseButton2ClickConnectionCount = 0x9dc;  // int
        inline constexpr uintptr_t MouseButton2DownConnectionCount = 0x9e0;  // int
        inline constexpr uintptr_t MouseButton2UpConnectionCount = 0x9e4;  // int
        inline constexpr uintptr_t Selected = 0x9ee;  // bool
    }
    namespace GuiLayerCollector {
        inline constexpr uintptr_t Enabled = 0x494;  // bool
        inline constexpr uintptr_t ResetOnSpawn = 0x495;  // bool
        inline constexpr uintptr_t TabKeyboardNavigation = 0x496;  // bool
        inline constexpr uintptr_t ZIndexBehavior = 0x490;  // Enums::ZIndexBehaviorEnum::ZIndexBehavior
    }
    namespace GuiObject {
        inline constexpr uintptr_t DragBeginConnectionCount = 0x540;  // int
        inline constexpr uintptr_t DragStoppedConnectionCount = 0x544;  // int
        inline constexpr uintptr_t Draggable = 0x57a;  // bool
        inline constexpr uintptr_t InputSink = 0x56c;  // Enums::InputSink
        inline constexpr uintptr_t Interactable = 0x57b;  // bool
        inline constexpr uintptr_t MouseEnterConnectionCount = 0x550;  // int
        inline constexpr uintptr_t MouseLeaveConnectionCount = 0x554;  // int
        inline constexpr uintptr_t MouseMovedConnectionCount = 0x558;  // int
        inline constexpr uintptr_t MouseWheelBackwardConnectionCount = 0x55c;  // int
        inline constexpr uintptr_t MouseWheelForwardConnectionCount = 0x560;  // int
        inline constexpr uintptr_t Position = 0x4e0;  // UDim2
        inline constexpr uintptr_t Rotation = 0x564;  // float
        inline constexpr uintptr_t SelectionImageObject = 0x4d0;
        inline constexpr uintptr_t Sink = 0x56c;  // Enums::InputSink
        inline constexpr uintptr_t Size = 0x500;  // UDim2
    }
    namespace GuiService {
        inline constexpr uintptr_t DisplayScalingMode = 0x128;  // Enums::DisplayScalingMode
        inline constexpr uintptr_t GuiNavigationEnabled = 0x134;  // bool
        inline constexpr uintptr_t TouchControlsEnabled = 0x136;  // bool
    }
    namespace GuiTextButton {
        inline constexpr uintptr_t Confidential = 0xcc;  // bool
        inline constexpr uintptr_t LocalizationMatchIdentifier = 0x20;
        inline constexpr uintptr_t LocalizationMatchedSourceText = 0x38;
    }
    namespace HandleAdornment {
        inline constexpr uintptr_t AdornCullingMode = 0x13c;  // AdornCullingMode
        inline constexpr uintptr_t AlwaysOnTop = 0x144;  // bool
        inline constexpr uintptr_t SizeRelativeOffset = 0x130;  // Vector3
    }
    namespace Handles {
        inline constexpr uintptr_t Faces = 0x104;  // Faces
        inline constexpr uintptr_t MouseButton1DownConnectionCount = 0x108;  // int
        inline constexpr uintptr_t MouseButton1UpConnectionCount = 0x10c;  // int
        inline constexpr uintptr_t MouseDragConnectionCount = 0x110;  // int
        inline constexpr uintptr_t MouseEnterConnectionCount = 0x114;  // int
        inline constexpr uintptr_t MouseLeaveConnectionCount = 0x118;  // int
        inline constexpr uintptr_t Style = 0x11c;  // Enums::HandlesStyleEnum::VisualStyle
    }
    namespace HapticEffect {
        inline constexpr uintptr_t Looped = 0xcc;  // bool
        inline constexpr uintptr_t Position = 0xb8;  // Vector3
        inline constexpr uintptr_t Radius = 0xc4;  // float
        inline constexpr uintptr_t Type = 0xc8;  // Enums::HapticEffectType
        inline constexpr uintptr_t WaveformData = 0xa0;  // BinaryString
    }
    namespace HiddenSurfaceRemovalAsset {
        inline constexpr uintptr_t HSRMeshIdData = 0xb0;  // BinaryString
    }
    namespace Highlight {
        inline constexpr uintptr_t DepthMode = 0xc8;  // Enums::HighlightDepthModeEnum::HighlightDepthMode
        inline constexpr uintptr_t Enabled = 0xdc;  // bool
        inline constexpr uintptr_t FillColor = 0xb0;  // Color3
        inline constexpr uintptr_t FillTransparency = 0xcc;  // float
        inline constexpr uintptr_t LineThickness = 0xd0;  // int
        inline constexpr uintptr_t OutlineColor = 0xbc;  // Color3
        inline constexpr uintptr_t OutlineTransparency = 0xd4;  // float
        inline constexpr uintptr_t ReservedId = 0xd8;  // Enums::ReservedHighlightId
    }
    namespace HopperBin {
        inline constexpr uintptr_t Active = 0x3ec;  // bool
        inline constexpr uintptr_t BinType = 0x3e8;  // Enums::BinTypeEnum::BinType
    }
    namespace HttpService {
        inline constexpr uintptr_t HttpEnabled = 0xa1;  // bool
    }
    namespace HumanoidDescription {
        inline constexpr uintptr_t BodyTypeScale = 0x130;  // float
        inline constexpr uintptr_t ClimbAnimation = 0xd0;  // int64
        inline constexpr uintptr_t DepthScale = 0x134;  // float
        inline constexpr uintptr_t Face = 0xd8;  // int64
        inline constexpr uintptr_t FallAnimation = 0xe0;  // int64
        inline constexpr uintptr_t GraphicTShirt = 0xe8;  // int64
        inline constexpr uintptr_t HeadScale = 0x138;  // float
        inline constexpr uintptr_t HeightScale = 0x13c;  // float
        inline constexpr uintptr_t IdleAnimation = 0xf0;  // int64
        inline constexpr uintptr_t JumpAnimation = 0xf8;  // int64
        inline constexpr uintptr_t MoodAnimation = 0x100;  // int64
        inline constexpr uintptr_t NumberEmotesLoaded = 0x140;  // int
        inline constexpr uintptr_t Pants = 0x108;  // int64
        inline constexpr uintptr_t ProportionScale = 0x144;  // float
        inline constexpr uintptr_t ResetIncludesBodyParts = 0x14c;  // bool
        inline constexpr uintptr_t RunAnimation = 0x110;  // int64
        inline constexpr uintptr_t Shirt = 0x118;  // int64
        inline constexpr uintptr_t StaticFacialAnimation = 0x14d;  // bool
        inline constexpr uintptr_t SwimAnimation = 0x120;  // int64
        inline constexpr uintptr_t UseAvatarSettings = 0x14e;  // bool
        inline constexpr uintptr_t WalkAnimation = 0x128;  // int64
        inline constexpr uintptr_t WidthScale = 0x148;  // float
    }
    namespace HumanoidRigDescription {
        inline constexpr uintptr_t Chest = 0x98;
        inline constexpr uintptr_t ChestRangeMax = 0x648;  // Vector3
        inline constexpr uintptr_t ChestRangeMin = 0x654;  // Vector3
        inline constexpr uintptr_t ChestSize = 0x858;  // float
        inline constexpr uintptr_t ChestTposeAdjustment = 0x1f8;  // CoordinateFrame
        inline constexpr uintptr_t HeadBase = 0xa8;
        inline constexpr uintptr_t HeadBaseRangeMax = 0x660;  // Vector3
        inline constexpr uintptr_t HeadBaseRangeMin = 0x66c;  // Vector3
        inline constexpr uintptr_t HeadBaseSize = 0x85c;  // float
        inline constexpr uintptr_t HeadBaseTposeAdjustment = 0x228;  // CoordinateFrame
        inline constexpr uintptr_t LeftAnkle = 0xb8;
        inline constexpr uintptr_t LeftAnkleRangeMax = 0x678;  // Vector3
        inline constexpr uintptr_t LeftAnkleRangeMin = 0x684;  // Vector3
        inline constexpr uintptr_t LeftAnkleSize = 0x860;  // float
        inline constexpr uintptr_t LeftAnkleTposeAdjustment = 0x258;  // CoordinateFrame
        inline constexpr uintptr_t LeftClavicle = 0xc8;
        inline constexpr uintptr_t LeftClavicleRangeMax = 0x690;  // Vector3
        inline constexpr uintptr_t LeftClavicleRangeMin = 0x69c;  // Vector3
        inline constexpr uintptr_t LeftClavicleSize = 0x864;  // float
        inline constexpr uintptr_t LeftClavicleTposeAdjustment = 0x288;  // CoordinateFrame
        inline constexpr uintptr_t LeftElbow = 0xd8;
        inline constexpr uintptr_t LeftElbowRangeMax = 0x6a8;  // Vector3
        inline constexpr uintptr_t LeftElbowRangeMin = 0x6b4;  // Vector3
        inline constexpr uintptr_t LeftElbowSize = 0x868;  // float
        inline constexpr uintptr_t LeftElbowTposeAdjustment = 0x2b8;  // CoordinateFrame
        inline constexpr uintptr_t LeftHip = 0xe8;
        inline constexpr uintptr_t LeftHipRangeMax = 0x6c0;  // Vector3
        inline constexpr uintptr_t LeftHipRangeMin = 0x6cc;  // Vector3
        inline constexpr uintptr_t LeftHipSize = 0x86c;  // float
        inline constexpr uintptr_t LeftHipTposeAdjustment = 0x2e8;  // CoordinateFrame
        inline constexpr uintptr_t LeftKnee = 0xf8;
        inline constexpr uintptr_t LeftKneeRangeMax = 0x6d8;  // Vector3
        inline constexpr uintptr_t LeftKneeRangeMin = 0x6e4;  // Vector3
        inline constexpr uintptr_t LeftKneeSize = 0x870;  // float
        inline constexpr uintptr_t LeftKneeTposeAdjustment = 0x318;  // CoordinateFrame
        inline constexpr uintptr_t LeftShoulder = 0x108;
        inline constexpr uintptr_t LeftShoulderRangeMax = 0x6f0;  // Vector3
        inline constexpr uintptr_t LeftShoulderRangeMin = 0x6fc;  // Vector3
        inline constexpr uintptr_t LeftShoulderSize = 0x874;  // float
        inline constexpr uintptr_t LeftShoulderTposeAdjustment = 0x348;  // CoordinateFrame
        inline constexpr uintptr_t LeftToeBase = 0x118;
        inline constexpr uintptr_t LeftToeBaseRangeMax = 0x708;  // Vector3
        inline constexpr uintptr_t LeftToeBaseRangeMin = 0x714;  // Vector3
        inline constexpr uintptr_t LeftToeBaseSize = 0x878;  // float
        inline constexpr uintptr_t LeftToeBaseTposeAdjustment = 0x378;  // CoordinateFrame
        inline constexpr uintptr_t LeftWrist = 0x128;
        inline constexpr uintptr_t LeftWristRangeMax = 0x720;  // Vector3
        inline constexpr uintptr_t LeftWristRangeMin = 0x72c;  // Vector3
        inline constexpr uintptr_t LeftWristSize = 0x87c;  // float
        inline constexpr uintptr_t LeftWristTposeAdjustment = 0x3a8;  // CoordinateFrame
        inline constexpr uintptr_t Neck = 0x138;
        inline constexpr uintptr_t NeckRangeMax = 0x738;  // Vector3
        inline constexpr uintptr_t NeckRangeMin = 0x744;  // Vector3
        inline constexpr uintptr_t NeckSize = 0x880;  // float
        inline constexpr uintptr_t NeckTposeAdjustment = 0x3d8;  // CoordinateFrame
        inline constexpr uintptr_t OriginOffset = 0x408;  // CoordinateFrame
        inline constexpr uintptr_t RightAnkle = 0x148;
        inline constexpr uintptr_t RightAnkleRangeMax = 0x750;  // Vector3
        inline constexpr uintptr_t RightAnkleRangeMin = 0x75c;  // Vector3
        inline constexpr uintptr_t RightAnkleSize = 0x884;  // float
        inline constexpr uintptr_t RightAnkleTposeAdjustment = 0x438;  // CoordinateFrame
        inline constexpr uintptr_t RightClavicle = 0x158;
        inline constexpr uintptr_t RightClavicleRangeMax = 0x768;  // Vector3
        inline constexpr uintptr_t RightClavicleRangeMin = 0x774;  // Vector3
        inline constexpr uintptr_t RightClavicleSize = 0x888;  // float
        inline constexpr uintptr_t RightClavicleTposeAdjustment = 0x468;  // CoordinateFrame
        inline constexpr uintptr_t RightElbow = 0x168;
        inline constexpr uintptr_t RightElbowRangeMax = 0x780;  // Vector3
        inline constexpr uintptr_t RightElbowRangeMin = 0x78c;  // Vector3
        inline constexpr uintptr_t RightElbowSize = 0x88c;  // float
        inline constexpr uintptr_t RightElbowTposeAdjustment = 0x498;  // CoordinateFrame
        inline constexpr uintptr_t RightHip = 0x178;
        inline constexpr uintptr_t RightHipRangeMax = 0x798;  // Vector3
        inline constexpr uintptr_t RightHipRangeMin = 0x7a4;  // Vector3
        inline constexpr uintptr_t RightHipSize = 0x890;  // float
        inline constexpr uintptr_t RightHipTposeAdjustment = 0x4c8;  // CoordinateFrame
        inline constexpr uintptr_t RightKnee = 0x188;
        inline constexpr uintptr_t RightKneeRangeMax = 0x7b0;  // Vector3
        inline constexpr uintptr_t RightKneeRangeMin = 0x7bc;  // Vector3
        inline constexpr uintptr_t RightKneeSize = 0x894;  // float
        inline constexpr uintptr_t RightKneeTposeAdjustment = 0x4f8;  // CoordinateFrame
        inline constexpr uintptr_t RightShoulder = 0x198;
        inline constexpr uintptr_t RightShoulderRangeMax = 0x7c8;  // Vector3
        inline constexpr uintptr_t RightShoulderRangeMin = 0x7d4;  // Vector3
        inline constexpr uintptr_t RightShoulderSize = 0x898;  // float
        inline constexpr uintptr_t RightShoulderTposeAdjustment = 0x528;  // CoordinateFrame
        inline constexpr uintptr_t RightToeBase = 0x1a8;
        inline constexpr uintptr_t RightToeBaseRangeMax = 0x7e0;  // Vector3
        inline constexpr uintptr_t RightToeBaseRangeMin = 0x7ec;  // Vector3
        inline constexpr uintptr_t RightToeBaseSize = 0x89c;  // float
        inline constexpr uintptr_t RightToeBaseTposeAdjustment = 0x558;  // CoordinateFrame
        inline constexpr uintptr_t RightWrist = 0x1b8;
        inline constexpr uintptr_t RightWristRangeMax = 0x7f8;  // Vector3
        inline constexpr uintptr_t RightWristRangeMin = 0x804;  // Vector3
        inline constexpr uintptr_t RightWristSize = 0x8a0;  // float
        inline constexpr uintptr_t RightWristTposeAdjustment = 0x588;  // CoordinateFrame
        inline constexpr uintptr_t Root = 0x1c8;
        inline constexpr uintptr_t RootRangeMax = 0x810;  // Vector3
        inline constexpr uintptr_t RootRangeMin = 0x81c;  // Vector3
        inline constexpr uintptr_t RootSize = 0x8a4;  // float
        inline constexpr uintptr_t RootTposeAdjustment = 0x5b8;  // CoordinateFrame
        inline constexpr uintptr_t Spine = 0x1d8;
        inline constexpr uintptr_t SpineRangeMax = 0x828;  // Vector3
        inline constexpr uintptr_t SpineRangeMin = 0x834;  // Vector3
        inline constexpr uintptr_t SpineSize = 0x8a8;  // float
        inline constexpr uintptr_t SpineTposeAdjustment = 0x5e8;  // CoordinateFrame
        inline constexpr uintptr_t Waist = 0x1e8;
        inline constexpr uintptr_t WaistRangeMax = 0x840;  // Vector3
        inline constexpr uintptr_t WaistRangeMin = 0x84c;  // Vector3
        inline constexpr uintptr_t WaistSize = 0x8ac;  // float
        inline constexpr uintptr_t WaistTposeAdjustment = 0x618;  // CoordinateFrame
    }
    namespace IkControl {
        inline constexpr uintptr_t ChainRoot = 0xa0;
        inline constexpr uintptr_t Enabled = 0x150;  // bool
        inline constexpr uintptr_t EndEffector = 0xb0;
        inline constexpr uintptr_t Pole = 0xc0;
        inline constexpr uintptr_t Priority = 0x140;  // int
        inline constexpr uintptr_t SmoothTime = 0x144;  // float
        inline constexpr uintptr_t Target = 0xd0;
        inline constexpr uintptr_t Type = 0x148;  // Enums::Type
        inline constexpr uintptr_t Weight = 0x14c;  // float
    }
    namespace ImageHandleAdornment {
        inline constexpr uintptr_t DoubleSided = 0x1c0;  // bool
        inline constexpr uintptr_t Size = 0x1b8;  // Vector2
    }
    namespace IncrementalPatchBuilder {
        inline constexpr uintptr_t AddPathsToBundle = 0xb0;  // bool
        inline constexpr uintptr_t BuildDebouncePeriod = 0x170;  // double
        inline constexpr uintptr_t HighCompression = 0xb1;  // bool
        inline constexpr uintptr_t SerializePatch = 0xb2;  // bool
        inline constexpr uintptr_t UseFileLevelCompressionInsteadOfChunk = 0xb3;  // bool
        inline constexpr uintptr_t ZstdCompression = 0xb4;  // bool
    }
    namespace InputAction {
        inline constexpr uintptr_t DisplayName = 0xa0;
        inline constexpr uintptr_t Enabled = 0xec;  // bool
        inline constexpr uintptr_t Type = 0xe8;  // Enums::InputActionType
    }
    namespace InputBinding {
        inline constexpr uintptr_t Backward = 0x11c;  // KeyCode
        inline constexpr uintptr_t ClampMagnitudeToOne = 0x158;  // bool
        inline constexpr uintptr_t Deadzone = 0x10c;  // NumberRange
        inline constexpr uintptr_t DisplayName = 0xc8;
        inline constexpr uintptr_t Down = 0x120;  // KeyCode
        inline constexpr uintptr_t Forward = 0x124;  // KeyCode
        inline constexpr uintptr_t KeyCode = 0x128;  // KeyCode
        inline constexpr uintptr_t Left = 0x12c;  // KeyCode
        inline constexpr uintptr_t PointerIndex = 0x130;  // int
        inline constexpr uintptr_t PressedThreshold = 0x134;  // float
        inline constexpr uintptr_t PrimaryModifier = 0x138;  // KeyCode
        inline constexpr uintptr_t ResponseCurve = 0x140;  // float
        inline constexpr uintptr_t Right = 0x144;  // KeyCode
        inline constexpr uintptr_t Scale = 0x148;  // float
        inline constexpr uintptr_t SecondaryModifier = 0x14c;  // KeyCode
        inline constexpr uintptr_t Type = 0x150;  // Enums::InputBindingType
        inline constexpr uintptr_t Up = 0x154;  // KeyCode
        inline constexpr uintptr_t Vector2Scale = 0x114;  // Vector2
        inline constexpr uintptr_t Vector3Scale = 0x100;  // Vector3
    }
    namespace InputContext {
        inline constexpr uintptr_t Enabled = 0xa4;  // bool
        inline constexpr uintptr_t Priority = 0xa0;  // int
        inline constexpr uintptr_t Sink = 0xa5;  // bool
    }
    namespace InputObject {
        inline constexpr uintptr_t Delta = 0xa0;  // Vector3
        inline constexpr uintptr_t KeyCode = 0xac;  // KeyCode
        inline constexpr uintptr_t UserInputState = 0xb0;  // Enums::UserInputStateEnum::UserInputState
        inline constexpr uintptr_t UserInputType = 0xb4;  // Enums::UserInputTypeEnum::UserInputType
    }
    namespace InsertService {
        inline constexpr uintptr_t AllowInsertFreeModels = 0xa1;  // bool
    }
    namespace IntConstrainedValue {
        inline constexpr uintptr_t MaxValue = 0xa0;  // int64
        inline constexpr uintptr_t MinValue = 0xa8;  // int64
    }
    namespace IntValue {
        inline constexpr uintptr_t Value = 0xa0;  // int64
    }
    namespace JointInstance {
        inline constexpr uintptr_t Enabled = 0xa0;  // bool
    }
    namespace Keyframe {
        inline constexpr uintptr_t Time = 0xa0;  // float
    }
    namespace KeyframeMarker {
        inline constexpr uintptr_t Value = 0xa0;
    }
    namespace KeyframeSequence {
        inline constexpr uintptr_t AuthoredHipHeight = 0xc0;  // float
    }
    namespace Light {
        inline constexpr uintptr_t Brightness = 0xb4;  // float
        inline constexpr uintptr_t Color = 0xa8;  // Color3
        inline constexpr uintptr_t Enabled = 0xb8;  // bool
        inline constexpr uintptr_t Shadows = 0xb9;  // bool
    }
    namespace Lighting {
        inline constexpr uintptr_t Ambient = 0xb8;  // Color3
        inline constexpr uintptr_t Brightness = 0x100;  // float
        inline constexpr uintptr_t ColorShift_Bottom = 0xc4;  // Color3
        inline constexpr uintptr_t ColorShift_Top = 0xd0;  // Color3
        inline constexpr uintptr_t EnvironmentDiffuseScale = 0x104;  // float
        inline constexpr uintptr_t EnvironmentSpecularScale = 0x108;  // float
        inline constexpr uintptr_t ExposureCompensation = 0x10c;  // float
        inline constexpr uintptr_t ExtendLightRangeTo120 = 0x110;  // Enums::RolloutState
        inline constexpr uintptr_t FogColor = 0xdc;  // Color3
        inline constexpr uintptr_t FogEnd = 0x114;  // float
        inline constexpr uintptr_t FogStart = 0x118;  // float
        inline constexpr uintptr_t GeographicLatitude = 0x11c;  // float
        inline constexpr uintptr_t GlobalShadows = 0x12c;  // bool
        inline constexpr uintptr_t LightingStyle = 0x120;  // LightingStyle
        inline constexpr uintptr_t OutdoorAmbient = 0xe8;  // Color3
        inline constexpr uintptr_t Outlines = 0x12d;  // bool
        inline constexpr uintptr_t PrioritizeLightingQuality = 0x12e;  // bool
        inline constexpr uintptr_t ShadowColor = 0xf4;  // Color3
        inline constexpr uintptr_t ShadowSoftness = 0x124;  // float
    }
    namespace LineHandleAdornment {
        inline constexpr uintptr_t Length = 0x18c;  // float
        inline constexpr uintptr_t Thickness = 0x190;  // float
    }
    namespace LocalizationService {
        inline constexpr uintptr_t ForcePlayModeGameLocaleId = 0xb0;
        inline constexpr uintptr_t ForcePlayModeRobloxLocaleId = 0xc8;
        inline constexpr uintptr_t GameSourceLanguageId = 0xe0;
        inline constexpr uintptr_t IsImageCaptureEnabled = 0x108;  // bool
        inline constexpr uintptr_t IsTextScraperRunning = 0x240;  // bool
        inline constexpr uintptr_t RobloxForcePlayModeGameLocaleId = 0xb0;
        inline constexpr uintptr_t RobloxForcePlayModeRobloxLocaleId = 0xc8;
        inline constexpr uintptr_t ShouldUseCloudTable = 0x109;  // bool
        inline constexpr uintptr_t ShouldUseImageLocalizationTable = 0x10a;  // bool
    }
    namespace LocalizationTable {
        inline constexpr uintptr_t DevelopmentLanguage = 0xa0;
        inline constexpr uintptr_t IsExemptFromUGCAnalytics = 0xc8;  // bool
        inline constexpr uintptr_t SourceLocaleId = 0xa0;
    }
    namespace LodDataEntity {
        inline constexpr uintptr_t EntityLodEnabled = 0x134;  // bool
        inline constexpr uintptr_t EntityModelSize = 0x118;  // Vector3
        inline constexpr uintptr_t EntityPosition = 0xe8;  // CoordinateFrame
        inline constexpr uintptr_t EntityScale = 0x124;  // Vector3
        inline constexpr uintptr_t EntityVisible = 0x135;  // bool
        inline constexpr uintptr_t IsSlimEnabled = 0x136;  // bool
        inline constexpr uintptr_t SlimReplicationTimestampSec = 0xe0;  // double
        inline constexpr uintptr_t TranscoderFailureReason = 0xa0;
        inline constexpr uintptr_t TranscoderStatus = 0x130;  // SlimTranscoderStatus
    }
    namespace LuaSourceContainer {
        inline constexpr uintptr_t CachedRemoteSource = 0xa0;  // ProtectedString
        inline constexpr uintptr_t CachedRemoteSourceLoadState = 0xd0;  // int
        inline constexpr uintptr_t HasAssociatedDrafts = 0xd4;  // bool
        inline constexpr uintptr_t IsDifferentFromFileSystem = 0xd5;  // bool
        inline constexpr uintptr_t ScriptGuid = 0xb8;
        inline constexpr uintptr_t isPlayerScript = 0xd6;  // bool
    }
    namespace MakeupDescription {
        inline constexpr uintptr_t AssetId = 0xa8;  // int64
        inline constexpr uintptr_t Instance = 0x98;
        inline constexpr uintptr_t MakeupType = 0xb0;  // MakeupType
        inline constexpr uintptr_t Order = 0xb4;  // int
    }
    namespace MaterialService {
        inline constexpr uintptr_t Use2022Materials = 0x478;  // bool
        inline constexpr uintptr_t Use2022MaterialsXml = 0x478;  // bool
    }
    namespace MaterialVariant {
        inline constexpr uintptr_t AlphaMode = 0x1b8;  // TexturePackAlphaMode
        inline constexpr uintptr_t AvgMetalness = 0x1bc;  // int
        inline constexpr uintptr_t AvgRoughness = 0x1c0;  // int
        inline constexpr uintptr_t BaseMaterial = 0x1c4;  // MaterialType
        inline constexpr uintptr_t ColorMapContent = 0xa0;  // Content
        inline constexpr uintptr_t EmissiveMaskContent = 0xc8;  // Content
        inline constexpr uintptr_t EmissiveStrength = 0x1c8;  // float
        inline constexpr uintptr_t EmissiveTint = 0x1ac;  // Color3
        inline constexpr uintptr_t MaterialPattern = 0x1cc;  // MaterialPattern
        inline constexpr uintptr_t MetalnessMapContent = 0xf0;  // Content
        inline constexpr uintptr_t NormalMapContent = 0x118;  // Content
        inline constexpr uintptr_t RoughnessMapContent = 0x140;  // Content
        inline constexpr uintptr_t StudsPerTile = 0x1d0;  // float
    }
    namespace MegaClusterInstance {
        inline constexpr uintptr_t AcquisitionMethod = 0x1c4;  // Enums::TerrainAcquisitionMethodEnum::TerrainAcquisitionMethod
        inline constexpr uintptr_t Decoration = 0x1e0;  // bool
        inline constexpr uintptr_t ExpandedTerrainResolved = 0x1e1;  // bool
        inline constexpr uintptr_t GrassLength = 0x1c8;  // float
        inline constexpr uintptr_t LastUsedModificationMethod = 0x1cc;  // Enums::TerrainAcquisitionMethodEnum::TerrainAcquisitionMethod
        inline constexpr uintptr_t SmoothVoxelsUpgraded = 0x1e2;  // bool
        inline constexpr uintptr_t WaterColor = 0x1b8;  // Color3
        inline constexpr uintptr_t WaterReflectance = 0x1d0;  // float
        inline constexpr uintptr_t WaterTransparency = 0x1d4;  // float
        inline constexpr uintptr_t WaterWaveSize = 0x1d8;  // float
        inline constexpr uintptr_t WaterWaveSpeed = 0x1dc;  // float
    }
    namespace MeshPart {
        inline constexpr uintptr_t DoubleSided = 0x33c;  // bool
        inline constexpr uintptr_t HasJointOffset = 0x33d;  // bool
        inline constexpr uintptr_t HasSkinnedMesh = 0x33e;  // bool
        inline constexpr uintptr_t InitialSize = 0x400;  // Vector3
        inline constexpr uintptr_t JointOffset = 0x328;  // Vector3
        inline constexpr uintptr_t MeshContent = 0x2d0;  // Content
        inline constexpr uintptr_t RenderFidelity = 0x334;  // RenderFidelity
        inline constexpr uintptr_t RenderFidelityReplicate = 0x334;  // RenderFidelity
        inline constexpr uintptr_t TextureContent = 0x2f8;  // Content
        inline constexpr uintptr_t VertexCount = 0x338;  // int
    }
    namespace Message {
        inline constexpr uintptr_t Text = 0xa0;
    }
    namespace MicroProfilerService {
        inline constexpr uintptr_t ContextLabel = 0xa8;
    }
    namespace ModelInstance {
        inline constexpr uintptr_t LevelOfDetail = 0x11c;  // ModelLevelOfDetail
        inline constexpr uintptr_t ModelMeshCFrame = 0xe0;  // CoordinateFrame
        inline constexpr uintptr_t ModelMeshData = 0xc8;  // SharedString
        inline constexpr uintptr_t ModelMeshSize = 0x110;  // Vector3
        inline constexpr uintptr_t ModelStreamingMode = 0x120;  // ModelStreamingMode
        inline constexpr uintptr_t Scale = 0x124;  // float
        inline constexpr uintptr_t ScaleFactor = 0x124;  // float
        inline constexpr uintptr_t SlimHash = 0xd0;  // SharedString
        inline constexpr uintptr_t WorldPivotData = 0xd8;  // OptionalCoordinateFrame
    }
    namespace ModuleScript {
        inline constexpr uintptr_t LinkedSource = 0xe8;  // ContentId
        inline constexpr uintptr_t Source = 0x108;  // ProtectedString
    }
    namespace Motor6D {
        inline constexpr uintptr_t EnableSkinning = 0x198;  // bool
        inline constexpr uintptr_t Transform = 0x168;  // CoordinateFrame
    }
    namespace NegateOperation {
        inline constexpr uintptr_t PreviousOperation = 0x3c0;  // NegateOperationHiddenHistory
    }
    namespace Noise {
        inline constexpr uintptr_t NoiseType = 0x98;  // NoiseType
        inline constexpr uintptr_t Seed = 0x9c;  // int
    }
    namespace NotificationService {
        inline constexpr uintptr_t SelectedTheme = 0xa8;
    }
    namespace PackageLink {
        inline constexpr uintptr_t AutoUpdate = 0x10c;  // bool
        inline constexpr uintptr_t CanAutoUpdate = 0x10d;  // bool
        inline constexpr uintptr_t DefaultName = 0xc8;
        inline constexpr uintptr_t HasNewVersion = 0x10e;  // bool
        inline constexpr uintptr_t ModifiedState = 0x108;  // int
        inline constexpr uintptr_t PackageContentSerialize = 0xa0;  // Content
        inline constexpr uintptr_t PackageGuid = 0xf8;  // int64
        inline constexpr uintptr_t SerializedDefaultAttributes = 0xe0;  // BinaryString
    }
    namespace Packages {
        inline constexpr uintptr_t IsDehydrated = 0xac;  // bool
        inline constexpr uintptr_t OverridesRecalculated = 0xad;  // bool
        inline constexpr uintptr_t ShellPackagesCount = 0xa4;  // int
        inline constexpr uintptr_t SkippedInstancesCount = 0xa8;  // int
    }
    namespace ParabolaAdornment {
        inline constexpr uintptr_t A = 0xe8;  // float
        inline constexpr uintptr_t B = 0xec;  // float
        inline constexpr uintptr_t C = 0xf0;  // float
        inline constexpr uintptr_t Range = 0xf4;  // float
        inline constexpr uintptr_t Thickness = 0xf8;  // float
    }
    namespace PartOperation {
        inline constexpr uintptr_t ChildData = 0x2f8;  // BinaryString
        inline constexpr uintptr_t ChildData2 = 0x348;  // SharedString
        inline constexpr uintptr_t ComponentIndex = 0x360;  // int
        inline constexpr uintptr_t DCDPropertyData = 0x310;  // CSGPropertyData
        inline constexpr uintptr_t InitialSize = 0x400;  // Vector3
        inline constexpr uintptr_t MeshData = 0x328;  // BinaryString
        inline constexpr uintptr_t MeshData2 = 0x358;  // SharedString
        inline constexpr uintptr_t OffCentered = 0x374;  // bool
        inline constexpr uintptr_t RenderFidelity = 0x368;  // RenderFidelity
        inline constexpr uintptr_t SmoothingAngle = 0x36c;  // float
        inline constexpr uintptr_t UsePartColor = 0x375;  // bool
    }
    namespace PartOperationAsset {
        inline constexpr uintptr_t MeshData = 0xb0;  // BinaryString
    }
    namespace ParticleEmitter2D {
        inline constexpr uintptr_t Acceleration = 0x1d8;  // Vector2
        inline constexpr uintptr_t Blend = 0x218;  // float
        inline constexpr uintptr_t Brightness = 0x21c;  // float
        inline constexpr uintptr_t Drag = 0x220;  // float
        inline constexpr uintptr_t EmissionAngle = 0x224;  // float
        inline constexpr uintptr_t EmissionMode = 0x228;  // ParticleEmitter2DEmissionMode
        inline constexpr uintptr_t EmissionOffset = 0x1e0;  // Vector2
        inline constexpr uintptr_t EmissionSpread = 0x1e8;  // Vector2
        inline constexpr uintptr_t Enabled = 0x250;  // bool
        inline constexpr uintptr_t FlipbookBlendFrames = 0x251;  // bool
        inline constexpr uintptr_t FlipbookFramerate = 0x1f0;  // NumberRange
        inline constexpr uintptr_t FlipbookLayout = 0x22c;  // ParticleFlipbookLayout
        inline constexpr uintptr_t FlipbookMode = 0x230;  // ParticleFlipbookMode
        inline constexpr uintptr_t FlipbookSizeX = 0x234;  // int
        inline constexpr uintptr_t FlipbookSizeY = 0x238;  // int
        inline constexpr uintptr_t FlipbookStartRandom = 0x252;  // bool
        inline constexpr uintptr_t Lifetime = 0x1f8;  // NumberRange
        inline constexpr uintptr_t LightEmission = 0x23c;  // float
        inline constexpr uintptr_t LockedToParent = 0x253;  // bool
        inline constexpr uintptr_t Rate = 0x240;  // float
        inline constexpr uintptr_t RotSpeed = 0x200;  // NumberRange
        inline constexpr uintptr_t Rotation = 0x208;  // NumberRange
        inline constexpr uintptr_t Speed = 0x210;  // NumberRange
        inline constexpr uintptr_t SpreadAngle = 0x244;  // float
        inline constexpr uintptr_t TimeScale = 0x248;  // float
        inline constexpr uintptr_t ZIndex = 0x24c;  // int
    }
    namespace PatchMapping {
        inline constexpr uintptr_t FlattenTree = 0xc8;  // bool
        inline constexpr uintptr_t PatchId = 0x98;
        inline constexpr uintptr_t TargetPath = 0xb0;
    }
    namespace Path2D {
        inline constexpr uintptr_t SelectedControlPoint = 0xd4;  // int
        inline constexpr uintptr_t Transparency = 0xdc;  // float
    }
    namespace PathfindingLink {
        inline constexpr uintptr_t IsBidirectional = 0xd8;  // bool
        inline constexpr uintptr_t Label = 0xa0;
    }
    namespace PathfindingModifier {
        inline constexpr uintptr_t Label = 0xa0;
        inline constexpr uintptr_t PassThrough = 0xb8;  // bool
    }
    namespace PhysicsActivitySensor {
        inline constexpr uintptr_t Position = 0x228;  // Vector3
        inline constexpr uintptr_t Size = 0x234;  // Vector3
    }
    namespace PlayerDataService {
        inline constexpr uintptr_t LoadFailureBehavior = 0xa4;  // Enums::PlayerDataLoadFailureBehavior
    }
    namespace PlayerEmulatorService {
        inline constexpr uintptr_t CustomPoliciesEnabled = 0xfc;  // bool
        inline constexpr uintptr_t EmulatedCountryCode = 0xb0;
        inline constexpr uintptr_t EmulatedGameLocale = 0xc8;
        inline constexpr uintptr_t PlayerEmulationEnabled = 0xfd;  // bool
        inline constexpr uintptr_t PseudolocalizationEnabled = 0xfe;  // bool
        inline constexpr uintptr_t SerializedEmulatedPolicyInfo = 0xe0;  // BinaryString
        inline constexpr uintptr_t TextElongationFactor = 0xf8;  // int
    }
    namespace PlayerGui {
        inline constexpr uintptr_t InputBindingMappingsRaw = 0x148;  // BinaryString
        inline constexpr uintptr_t ScreenOrientation = 0x174;  // Enums::ScreenOrientationEnum::ScreenOrientation
    }
    namespace PlayerListConfiguration {
        inline constexpr uintptr_t Open = 0x96;  // bool
    }
    namespace Plugin {
        inline constexpr uintptr_t DisableUIDragDetectorDrags = 0xc4;  // bool
        inline constexpr uintptr_t IsDebuggable = 0xc5;  // bool
        inline constexpr uintptr_t UsesAssetInsertionDrag = 0xc6;  // bool
    }
    namespace PluginAction {
        inline constexpr uintptr_t Checked = 0x100;  // bool
        inline constexpr uintptr_t DefaultShortcut = 0xd0;
        inline constexpr uintptr_t Enabled = 0x101;  // bool
        inline constexpr uintptr_t Text = 0xe8;
        inline constexpr uintptr_t Visible = 0x102;  // bool
    }
    namespace PluginCapabilities {
        inline constexpr uintptr_t Manifest = 0x98;
    }
    namespace PluginGui {
        inline constexpr uintptr_t Title = 0x770;
    }
    namespace PluginMenu {
        inline constexpr uintptr_t Icon = 0xd0;
        inline constexpr uintptr_t Title = 0xe8;
        inline constexpr uintptr_t Visible = 0x100;  // bool
    }
    namespace PluginToolbarButton {
        inline constexpr uintptr_t ClickableWhenViewportHidden = 0x100;  // bool
        inline constexpr uintptr_t Enabled = 0x101;  // bool
    }
    namespace PointLight {
        inline constexpr uintptr_t Range = 0xbc;  // float
    }
    namespace PolicyService {
        inline constexpr uintptr_t IsLuobuServer = 0xa4;  // Enums::TriStateBoolean
        inline constexpr uintptr_t LuobuWhitelisted = 0xa8;  // Enums::TriStateBoolean
    }
    namespace PoseBase {
        inline constexpr uintptr_t EasingDirection = 0xa0;  // Pose::PoseEasingDirection
        inline constexpr uintptr_t EasingStyle = 0xa4;  // Pose::PoseEasingStyle
        inline constexpr uintptr_t Weight = 0xa8;  // float
    }
    namespace PostEffect {
        inline constexpr uintptr_t Enabled = 0x95;  // bool
    }
    namespace ProceduralModel {
        inline constexpr uintptr_t Dirty = 0x324;  // bool
        inline constexpr uintptr_t Size = 0x318;  // Vector3
    }
    namespace ProximityPrompt {
        inline constexpr uintptr_t ActionText = 0x98;
        inline constexpr uintptr_t AutoLocalize = 0x10c;  // bool
        inline constexpr uintptr_t ClickablePrompt = 0x10d;  // bool
        inline constexpr uintptr_t Enabled = 0x10e;  // bool
        inline constexpr uintptr_t Exclusivity = 0xf0;  // Enums::ProximityPromptExclusivityEnum::ProximityPromptExclusivity
        inline constexpr uintptr_t GamepadKeyCode = 0xf4;  // KeyCode
        inline constexpr uintptr_t HoldDuration = 0xf8;  // float
        inline constexpr uintptr_t KeyboardKeyCode = 0xfc;  // KeyCode
        inline constexpr uintptr_t MaxActivationDistance = 0x100;  // float
        inline constexpr uintptr_t MaxIndicatorDistance = 0x104;  // float
        inline constexpr uintptr_t ObjectText = 0xb0;
        inline constexpr uintptr_t RequiresLineOfSight = 0x10f;  // bool
        inline constexpr uintptr_t Style = 0x108;  // Enums::ProximityPromptStyleEnum::ProximityPromptStyle
        inline constexpr uintptr_t UIOffset = 0xe8;  // Vector2
    }
    namespace ProximityPromptService {
        inline constexpr uintptr_t Enabled = 0xc0;  // bool
        inline constexpr uintptr_t MaxIndicatorsVisible = 0xb8;  // int
        inline constexpr uintptr_t MaxPromptsVisible = 0xbc;  // int
    }
    namespace PyramidHandleAdornment {
        inline constexpr uintptr_t DoubleSided = 0x19c;  // bool
        inline constexpr uintptr_t Height = 0x18c;  // float
        inline constexpr uintptr_t Shading = 0x190;  // Enums::AdornShading
        inline constexpr uintptr_t Sides = 0x194;  // int
        inline constexpr uintptr_t Size = 0x198;  // float
    }
    namespace RVideo_VideoDeviceInput {
        inline constexpr uintptr_t Active = 0x170;  // bool
        inline constexpr uintptr_t CameraId = 0x170;
        inline constexpr uintptr_t CaptureQuality = 0x180;
    }
    namespace RealTimeAnimation_RTAnimationTracker {
        inline constexpr uintptr_t Active = 0x11c;  // bool
        inline constexpr uintptr_t EnableFallbackAudioInput = 0x11d;  // bool
        inline constexpr uintptr_t SessionName = 0xf0;
        inline constexpr uintptr_t TrackerType = 0x118;
    }
    namespace RealtimeMedia {
        inline constexpr uintptr_t ForwardInput = 0x131;  // bool
    }
    namespace RenderingTest {
        inline constexpr uintptr_t CFrame = 0xd8;  // CoordinateFrame
        inline constexpr uintptr_t ComparisonDiffThreshold = 0x1c0;  // int
        inline constexpr uintptr_t ComparisonMethod = 0x1c8;  // RenderingTestComparisonMethod
        inline constexpr uintptr_t ComparisonPsnrThreshold = 0x1c4;  // float
        inline constexpr uintptr_t Description = 0xa0;
        inline constexpr uintptr_t FieldOfView = 0x108;  // float
        inline constexpr uintptr_t PerfTest = 0x114;  // bool
        inline constexpr uintptr_t Position = 0xfc;  // Vector3
        inline constexpr uintptr_t QualityAuto = 0x1b8;  // bool
        inline constexpr uintptr_t QualityLevel = 0x1bc;  // int
        inline constexpr uintptr_t RenderingTestFrameCount = 0x10c;  // int
        inline constexpr uintptr_t ShouldSkip = 0x115;  // bool
        inline constexpr uintptr_t Ticket = 0xb8;
        inline constexpr uintptr_t Timeout = 0x110;  // int
    }
    namespace RobloxSerializableInstance {
        inline constexpr uintptr_t Data = 0x98;  // BinaryString
    }
    namespace Rocket {
        inline constexpr uintptr_t Active = 0x2c0;  // bool
        inline constexpr uintptr_t CartoonFactor = 0x2a0;  // float
        inline constexpr uintptr_t MaxSpeed = 0x2a4;  // float
        inline constexpr uintptr_t MaxThrust = 0x2a8;  // float
        inline constexpr uintptr_t MaxTorque = 0x288;  // Vector3
        inline constexpr uintptr_t Target = 0x278;
        inline constexpr uintptr_t TargetOffset = 0x294;  // Vector3
        inline constexpr uintptr_t TargetRadius = 0x2ac;  // float
        inline constexpr uintptr_t ThrustD = 0x2b0;  // float
        inline constexpr uintptr_t ThrustP = 0x2b4;  // float
        inline constexpr uintptr_t TurnD = 0x2b8;  // float
        inline constexpr uintptr_t TurnP = 0x2bc;  // float
    }
    namespace RolloutValidation {
        inline constexpr uintptr_t AdditionalFluffOne = 0x188;  // int
        inline constexpr uintptr_t AdditionalFluffThree = 0x18c;  // float
        inline constexpr uintptr_t AdditionalFluffTwo = 0x318;  // bool
        inline constexpr uintptr_t CreationVersion = 0x190;  // int
        inline constexpr uintptr_t FirstBinaryString = 0xb0;  // BinaryString
        inline constexpr uintptr_t FirstSharedExpectedValue = 0xc8;
        inline constexpr uintptr_t FirstSharedString = 0x170;  // SharedString
        inline constexpr uintptr_t GenerationStrategy = 0x194;  // int
        inline constexpr uintptr_t SecondBinaryExpectedValue = 0xe0;
        inline constexpr uintptr_t SecondBinaryString = 0xf8;  // BinaryString
        inline constexpr uintptr_t SecondSharedExpectedValue = 0x110;
        inline constexpr uintptr_t SecondSharedString = 0x178;  // SharedString
        inline constexpr uintptr_t ThirdBinaryExpectedValue = 0x128;
        inline constexpr uintptr_t ThirdBinaryString = 0x140;  // BinaryString
        inline constexpr uintptr_t ThirdSharedExpectedValue = 0x158;
        inline constexpr uintptr_t ThirdSharedString = 0x180;  // SharedString
    }
    namespace RunService {
        inline constexpr uintptr_t RunState = 0xc0;  // RunState
    }
    namespace Safety_SafetyService {
        inline constexpr uintptr_t IsCaptureModeForReport = 0xa1;  // bool
    }
    namespace ScreenGui {
        inline constexpr uintptr_t ClipToDeviceSafeArea = 0x6a4;  // bool
        inline constexpr uintptr_t DisplayOrder = 0x698;  // int
        inline constexpr uintptr_t IgnoresTitleBarReservation = 0x6a5;  // bool
        inline constexpr uintptr_t OnTopOfCoreBlur = 0x6a6;  // bool
        inline constexpr uintptr_t SafeAreaCompatibility = 0x69c;  // SafeAreaCompatMode
        inline constexpr uintptr_t ScreenInsets = 0x6a0;  // ScreenInsetsType
    }
    namespace ScreenshotHud {
        inline constexpr uintptr_t CameraButtonPosition = 0xc0;  // UDim2
        inline constexpr uintptr_t CloseButtonPosition = 0xd0;  // UDim2
        inline constexpr uintptr_t CloseWhenScreenshotTaken = 0xe4;  // bool
        inline constexpr uintptr_t ExperienceNameOverlayEnabled = 0xe5;  // bool
        inline constexpr uintptr_t HideCoreGuiForCaptures = 0xe6;  // bool
        inline constexpr uintptr_t HidePlayerGuiForCaptures = 0xe7;  // bool
        inline constexpr uintptr_t OverlayFont = 0xe0;  // Text::Font
        inline constexpr uintptr_t UsernameOverlayEnabled = 0xe8;  // bool
        inline constexpr uintptr_t Visible = 0xe9;  // bool
    }
    namespace Script {
        inline constexpr uintptr_t Source = 0x160;  // ProtectedString
    }
    namespace ScriptContext {
        inline constexpr uintptr_t ScriptsDisabled = 0xa1;  // bool
    }
    namespace Scripting_DebuggerBreakpoint {
        inline constexpr uintptr_t ContinueExecution = 0xa4;  // bool
        inline constexpr uintptr_t IsEnabled = 0xa5;  // bool
        inline constexpr uintptr_t isContextDependentBreakpoint = 0xa6;  // bool
    }
    namespace ScrollingFrame {
        inline constexpr uintptr_t CanvasPosition = 0xa64;  // Vector2
        inline constexpr uintptr_t ScrollRate = 0xa94;  // float
        inline constexpr uintptr_t SmoothScroll = 0xaa5;  // bool
    }
    namespace Selection {
        inline constexpr uintptr_t ShowActiveInstanceHighlight = 0xb4;  // bool
    }
    namespace SelectionBox {
        inline constexpr uintptr_t LineThickness = 0xfc;  // float
        inline constexpr uintptr_t StudioSelectionBox = 0x104;  // bool
        inline constexpr uintptr_t SurfaceColor = 0xf0;  // BrickColor
        inline constexpr uintptr_t SurfaceColor3 = 0xf0;  // Color3
        inline constexpr uintptr_t SurfaceTransparency = 0x100;  // float
    }
    namespace SelectionPointLasso {
        inline constexpr uintptr_t Point = 0xf0;  // Vector3
    }
    namespace SelectionSphere {
        inline constexpr uintptr_t SurfaceColor = 0xf0;  // BrickColor
        inline constexpr uintptr_t SurfaceColor3 = 0xf0;  // Color3
        inline constexpr uintptr_t SurfaceTransparency = 0xfc;  // float
    }
    namespace SelfViewConfiguration {
        inline constexpr uintptr_t Open = 0x96;  // bool
    }
    namespace SensorBase {
        inline constexpr uintptr_t UpdateType = 0x98;  // SensorUpdateType
    }
    namespace ServerScriptService {
        inline constexpr uintptr_t LoadStringEnabled = 0xb0;  // bool
    }
    namespace ShirtGraphic {
        inline constexpr uintptr_t Color3 = 0xd0;  // Color3
    }
    namespace SkateboardPlatform {
        inline constexpr uintptr_t MoveState = 0x200;  // Enums::MoveStateEnum::MoveState
        inline constexpr uintptr_t Steer = 0x204;  // int
        inline constexpr uintptr_t StickyWheels = 0x20c;  // bool
        inline constexpr uintptr_t Throttle = 0x208;  // int
    }
    namespace Skin {
        inline constexpr uintptr_t SkinColor = 0xa8;  // BrickColor
    }
    namespace Sky {
        inline constexpr uintptr_t CelestialBodiesShown = 0x1f8;  // bool
        inline constexpr uintptr_t MoonAngularSize = 0x1ec;  // float
        inline constexpr uintptr_t SkyboxOrientation = 0x1e0;  // Vector3
        inline constexpr uintptr_t StarCount = 0x1f0;  // int
        inline constexpr uintptr_t SunAngularSize = 0x1f4;  // float
    }
    namespace SlimAnimationDataEntity {
        inline constexpr uintptr_t BoneParentIndices = 0x98;  // BinaryString
        inline constexpr uintptr_t EntityScale = 0xd8;  // double
        inline constexpr uintptr_t Handle = 0xe8;  // int
        inline constexpr uintptr_t IsSlimEnabled = 0xf4;  // bool
        inline constexpr uintptr_t NumBones = 0xec;  // int
        inline constexpr uintptr_t RootIndex = 0xf0;  // int
        inline constexpr uintptr_t SlimInstanceHashes = 0xb0;  // BinaryString
        inline constexpr uintptr_t SlimReplicationTimestampSec = 0xe0;  // double
    }
    namespace Smoke {
        inline constexpr uintptr_t Color = 0xa0;  // Color3
        inline constexpr uintptr_t Enabled = 0xc0;  // bool
        inline constexpr uintptr_t LocalTransparencyModifier = 0xac;  // float
        inline constexpr uintptr_t Opacity = 0xb0;  // float
        inline constexpr uintptr_t RiseVelocity = 0xb4;  // float
        inline constexpr uintptr_t Size = 0xb8;  // float
        inline constexpr uintptr_t TimeScale = 0xbc;  // float
        inline constexpr uintptr_t opacity_xml = 0xb0;  // float
        inline constexpr uintptr_t riseVelocity_xml = 0xb4;  // float
        inline constexpr uintptr_t size_xml = 0xb8;  // float
    }
    namespace Soundscape_AudioAnalyzer {
        inline constexpr uintptr_t SpectrumEnabled = 0x124;  // bool
        inline constexpr uintptr_t WindowSize = 0x120;
    }
    namespace Soundscape_AudioChannelMixer {
        inline constexpr uintptr_t Layout = 0x120;  // Enums::AudioChannelLayout
    }
    namespace Soundscape_AudioChannelSplitter {
        inline constexpr uintptr_t Layout = 0x120;  // Enums::AudioChannelLayout
    }
    namespace Soundscape_AudioChorus {
        inline constexpr uintptr_t Bypass = 0x12c;  // bool
        inline constexpr uintptr_t Depth = 0x120;  // float
        inline constexpr uintptr_t Mix = 0x124;  // float
        inline constexpr uintptr_t Rate = 0x128;  // float
    }
    namespace Soundscape_AudioCompressor {
        inline constexpr uintptr_t Attack = 0x120;  // float
        inline constexpr uintptr_t Bypass = 0x134;  // bool
        inline constexpr uintptr_t MakeupGain = 0x124;  // float
        inline constexpr uintptr_t Ratio = 0x128;  // float
        inline constexpr uintptr_t Release = 0x12c;  // float
        inline constexpr uintptr_t Threshold = 0x130;  // float
    }
    namespace Soundscape_AudioDeviceInput {
        inline constexpr uintptr_t AccessType = 0x158;
        inline constexpr uintptr_t Active = 0x160;  // bool
        inline constexpr uintptr_t DictationEnabled = 0x161;  // bool
        inline constexpr uintptr_t EchoCancellation = 0x162;  // bool
        inline constexpr uintptr_t GainControl = 0x163;  // bool
        inline constexpr uintptr_t Muted = 0x164;  // bool
        inline constexpr uintptr_t MutedByLocalUser = 0x165;  // bool
        inline constexpr uintptr_t NoiseSuppression = 0x166;  // bool
        inline constexpr uintptr_t Streaming = 0x167;  // bool
        inline constexpr uintptr_t Volume = 0x15c;  // float
    }
    namespace Soundscape_AudioDistortion {
        inline constexpr uintptr_t Bypass = 0x124;  // bool
        inline constexpr uintptr_t Level = 0x120;  // float
    }
    namespace Soundscape_AudioEcho {
        inline constexpr uintptr_t Bypass = 0x134;  // bool
        inline constexpr uintptr_t DelayTime = 0x120;  // float
        inline constexpr uintptr_t DryLevel = 0x124;  // float
        inline constexpr uintptr_t Feedback = 0x128;  // float
        inline constexpr uintptr_t RampTime = 0x12c;  // float
        inline constexpr uintptr_t WetLevel = 0x130;  // float
    }
    namespace Soundscape_AudioEmitter {
        inline constexpr uintptr_t AcousticSimulationEnabled = 0x168;  // bool
        inline constexpr uintptr_t AudioInteractionGroup = 0x138;
        inline constexpr uintptr_t DiffractionEnabled = 0x150;  // Enums::SimulationMode
        inline constexpr uintptr_t DistanceAttenuationBounds = 0x148;  // NumberRange
        inline constexpr uintptr_t DistanceAttenuationMode = 0x154;
        inline constexpr uintptr_t OcclusionEnabled = 0x158;  // Enums::SimulationMode
        inline constexpr uintptr_t PositionType = 0x15c;  // Enums::EmitterPositionType
        inline constexpr uintptr_t ReverbEnabled = 0x160;  // Enums::SimulationMode
        inline constexpr uintptr_t SimulationFidelity = 0x164;  // Enums::AudioSimulationFidelity
    }
    namespace Soundscape_AudioEqualizer {
        inline constexpr uintptr_t Bypass = 0x134;  // bool
        inline constexpr uintptr_t HighGain = 0x128;  // float
        inline constexpr uintptr_t LowGain = 0x12c;  // float
        inline constexpr uintptr_t MidGain = 0x130;  // float
        inline constexpr uintptr_t MidRange = 0x120;  // NumberRange
    }
    namespace Soundscape_AudioFader {
        inline constexpr uintptr_t Bypass = 0x124;  // bool
        inline constexpr uintptr_t Volume = 0x120;  // float
    }
    namespace Soundscape_AudioFilter {
        inline constexpr uintptr_t Bypass = 0x130;  // bool
        inline constexpr uintptr_t FilterType = 0x120;
        inline constexpr uintptr_t Frequency = 0x124;  // float
        inline constexpr uintptr_t Gain = 0x128;  // float
        inline constexpr uintptr_t Q = 0x12c;  // float
    }
    namespace Soundscape_AudioFlanger {
        inline constexpr uintptr_t Bypass = 0x12c;  // bool
        inline constexpr uintptr_t Depth = 0x120;  // float
        inline constexpr uintptr_t Mix = 0x124;  // float
        inline constexpr uintptr_t Rate = 0x128;  // float
    }
    namespace Soundscape_AudioGate {
        inline constexpr uintptr_t Attack = 0x128;  // float
        inline constexpr uintptr_t Bypass = 0x130;  // bool
        inline constexpr uintptr_t Release = 0x12c;  // float
        inline constexpr uintptr_t Threshold = 0x120;  // NumberRange
    }
    namespace Soundscape_AudioLimiter {
        inline constexpr uintptr_t Bypass = 0x128;  // bool
        inline constexpr uintptr_t MaxLevel = 0x120;  // float
        inline constexpr uintptr_t Release = 0x124;  // float
    }
    namespace Soundscape_AudioListener {
        inline constexpr uintptr_t AcousticSimulationEnabled = 0x15c;  // bool
        inline constexpr uintptr_t AudioInteractionGroup = 0x138;
        inline constexpr uintptr_t DiffractionEnabled = 0x148;  // Enums::SimulationMode
        inline constexpr uintptr_t OcclusionEnabled = 0x14c;  // Enums::SimulationMode
        inline constexpr uintptr_t PositionType = 0x150;  // Enums::ListenerPositionType
        inline constexpr uintptr_t ReverbEnabled = 0x154;  // Enums::SimulationMode
        inline constexpr uintptr_t SimulationFidelity = 0x158;  // Enums::AudioSimulationFidelity
    }
    namespace Soundscape_AudioPitchShifter {
        inline constexpr uintptr_t Bypass = 0x128;  // bool
        inline constexpr uintptr_t Pitch = 0x120;  // float
        inline constexpr uintptr_t WindowSize = 0x124;
    }
    namespace Soundscape_AudioPlayer {
        inline constexpr uintptr_t Asset = 0x128;  // ContentId
        inline constexpr uintptr_t AssetRepresentation = 0x150;  // AssetRepresentation
        inline constexpr uintptr_t AudioContent = 0x128;  // Content
        inline constexpr uintptr_t AutoLoad = 0x158;  // bool
        inline constexpr uintptr_t AutoPlay = 0x159;  // bool
        inline constexpr uintptr_t IsPlaying = 0x15a;  // bool
        inline constexpr uintptr_t LoopRegion = 0x140;  // NumberRange
        inline constexpr uintptr_t Looping = 0x15b;  // bool
        inline constexpr uintptr_t PlaybackRegion = 0x148;  // NumberRange
        inline constexpr uintptr_t PlaybackSpeed = 0x130;  // double
        inline constexpr uintptr_t TimePosition = 0x138;  // double
        inline constexpr uintptr_t Volume = 0x154;  // float
    }
    namespace Soundscape_AudioRecorder {
        inline constexpr uintptr_t IsRecording = 0x120;  // bool
    }
    namespace Soundscape_AudioReverb {
        inline constexpr uintptr_t Bypass = 0x150;  // bool
        inline constexpr uintptr_t DecayRatio = 0x120;  // float
        inline constexpr uintptr_t DecayTime = 0x124;  // float
        inline constexpr uintptr_t Density = 0x128;  // float
        inline constexpr uintptr_t Diffusion = 0x12c;  // float
        inline constexpr uintptr_t DryLevel = 0x130;  // float
        inline constexpr uintptr_t EarlyDelayTime = 0x134;  // float
        inline constexpr uintptr_t HighCutFrequency = 0x138;  // float
        inline constexpr uintptr_t LateDelayTime = 0x13c;  // float
        inline constexpr uintptr_t LowShelfFrequency = 0x140;  // float
        inline constexpr uintptr_t LowShelfGain = 0x144;  // float
        inline constexpr uintptr_t ReferenceFrequency = 0x148;  // float
        inline constexpr uintptr_t WetLevel = 0x14c;  // float
    }
    namespace Soundscape_AudioSpeechToText {
        inline constexpr uintptr_t DictationEnabled = 0x168;  // bool
        inline constexpr uintptr_t DisableVoiceDetection = 0x169;  // bool
        inline constexpr uintptr_t EnableVolumeCheck = 0x16a;  // bool
        inline constexpr uintptr_t Enabled = 0x16b;  // bool
        inline constexpr uintptr_t Locale = 0x120;
        inline constexpr uintptr_t Streaming = 0x16c;  // bool
        inline constexpr uintptr_t Text = 0x138;
        inline constexpr uintptr_t UsageType = 0x150;
        inline constexpr uintptr_t VoiceDetectedOverride = 0x16e;  // bool
    }
    namespace Soundscape_AudioTextToSpeech {
        inline constexpr uintptr_t AutoLocalize = 0x168;  // bool
        inline constexpr uintptr_t IsPlaying = 0x169;  // bool
        inline constexpr uintptr_t Looping = 0x16a;  // bool
        inline constexpr uintptr_t Pitch = 0x158;  // float
        inline constexpr uintptr_t PlaybackSpeed = 0x15c;  // float
        inline constexpr uintptr_t Speed = 0x160;  // float
        inline constexpr uintptr_t Text = 0x120;
        inline constexpr uintptr_t TimePosition = 0x150;  // double
        inline constexpr uintptr_t VoiceId = 0x138;
        inline constexpr uintptr_t Volume = 0x164;  // float
    }
    namespace Soundscape_AudioTremolo {
        inline constexpr uintptr_t Bypass = 0x138;  // bool
        inline constexpr uintptr_t Depth = 0x120;  // float
        inline constexpr uintptr_t Duty = 0x124;  // float
        inline constexpr uintptr_t Frequency = 0x128;  // float
        inline constexpr uintptr_t Shape = 0x12c;  // float
        inline constexpr uintptr_t Skew = 0x130;  // float
        inline constexpr uintptr_t Square = 0x134;  // float
    }
    namespace Soundscape_AudioWindSynthesizer {
        inline constexpr uintptr_t Enabled = 0x134;  // bool
        inline constexpr uintptr_t PositionType = 0x128;
        inline constexpr uintptr_t Profile = 0x12c;
        inline constexpr uintptr_t Volume = 0x130;  // float
    }
    namespace Soundscape_ChannelSelectorSoundEffect {
        inline constexpr uintptr_t Channel = 0xe8;  // int
    }
    namespace Soundscape_ChorusSoundEffect {
        inline constexpr uintptr_t Depth = 0xe0;  // float
        inline constexpr uintptr_t Mix = 0xe4;  // float
        inline constexpr uintptr_t Rate = 0xe8;  // float
    }
    namespace Soundscape_CompressorSoundEffect {
        inline constexpr uintptr_t Attack = 0xf0;  // float
        inline constexpr uintptr_t GainMakeup = 0xf4;  // float
        inline constexpr uintptr_t Ratio = 0xf8;  // float
        inline constexpr uintptr_t Release = 0xfc;  // float
        inline constexpr uintptr_t Threshold = 0x100;  // float
    }
    namespace Soundscape_DistortionSoundEffect {
        inline constexpr uintptr_t Level = 0xe0;  // float
    }
    namespace Soundscape_EchoSoundEffect {
        inline constexpr uintptr_t Delay = 0xe0;  // float
        inline constexpr uintptr_t DryLevel = 0xe4;  // float
        inline constexpr uintptr_t Feedback = 0xe8;  // float
        inline constexpr uintptr_t WetLevel = 0xec;  // float
    }
    namespace Soundscape_EqualizerSoundEffect {
        inline constexpr uintptr_t HighGain = 0xe0;  // float
        inline constexpr uintptr_t LowGain = 0xe4;  // float
        inline constexpr uintptr_t MidGain = 0xe8;  // float
    }
    namespace Soundscape_FlangeSoundEffect {
        inline constexpr uintptr_t Depth = 0xe0;  // float
        inline constexpr uintptr_t Mix = 0xe4;  // float
        inline constexpr uintptr_t Rate = 0xe8;  // float
    }
    namespace Soundscape_PitchShiftSoundEffect {
        inline constexpr uintptr_t Octave = 0xe0;  // float
    }
    namespace Soundscape_ReverbSoundEffect {
        inline constexpr uintptr_t DecayTime = 0xe0;  // float
        inline constexpr uintptr_t Density = 0xe4;  // float
        inline constexpr uintptr_t Diffusion = 0xe8;  // float
        inline constexpr uintptr_t DryLevel = 0xec;  // float
        inline constexpr uintptr_t WetLevel = 0xf0;  // float
    }
    namespace Soundscape_Sound {
        inline constexpr uintptr_t AcousticSimulationEnabled = 0x11c;  // bool
        inline constexpr uintptr_t AssetRepresentation = 0xe8;  // AssetRepresentation
        inline constexpr uintptr_t EmitterSize = 0x104;  // float
        inline constexpr uintptr_t LoopRegion = 0xd8;  // NumberRange
        inline constexpr uintptr_t Looped = 0x11d;  // bool
        inline constexpr uintptr_t MaxDistance = 0x100;  // float
        inline constexpr uintptr_t MinDistance = 0x104;  // float
        inline constexpr uintptr_t Pitch = 0xfc;  // float
        inline constexpr uintptr_t PlayOnRemove = 0x11e;  // bool
        inline constexpr uintptr_t PlaybackRegion = 0xe0;  // NumberRange
        inline constexpr uintptr_t PlaybackRegionsEnabled = 0x11f;  // bool
        inline constexpr uintptr_t PlaybackSpeed = 0xfc;  // float
        inline constexpr uintptr_t Playing = 0x120;  // bool
        inline constexpr uintptr_t PlayingReplicator = 0x120;  // bool
        inline constexpr uintptr_t RollOffMaxDistance = 0x100;  // float
        inline constexpr uintptr_t RollOffMinDistance = 0x104;  // float
        inline constexpr uintptr_t RollOffMode = 0x108;
        inline constexpr uintptr_t TimePosition = 0x1f0;  // double
        inline constexpr uintptr_t TimePositionReplicator = 0x1f0;  // double
        inline constexpr uintptr_t UsageContextPermission = 0x10c;  // UsageContext
        inline constexpr uintptr_t Volume = 0x110;  // float
        inline constexpr uintptr_t xmlRead_MaxDistance_3 = 0x100;  // float
        inline constexpr uintptr_t xmlRead_MinDistance_3 = 0x104;  // float
    }
    namespace Soundscape_SoundEffect {
        inline constexpr uintptr_t Enabled = 0xa4;  // bool
        inline constexpr uintptr_t Priority = 0xa0;  // int
    }
    namespace Soundscape_SoundGroup {
        inline constexpr uintptr_t Volume = 0xa0;  // float
    }
    namespace Soundscape_SoundService {
        inline constexpr uintptr_t AcousticSimulationEnabled = 0x160;  // bool
        inline constexpr uintptr_t AmbientReverb = 0x138;
        inline constexpr uintptr_t AudioApiByDefault = 0x13c;  // Enums::RolloutState
        inline constexpr uintptr_t CharacterSoundsUseNewApi = 0x140;  // Enums::RolloutState
        inline constexpr uintptr_t DefaultListenerLocation = 0x148;
        inline constexpr uintptr_t DiffractionEnabled = 0x161;  // bool
        inline constexpr uintptr_t DistanceFactor = 0x14c;  // float
        inline constexpr uintptr_t DopplerScale = 0x150;  // float
        inline constexpr uintptr_t IsNewExpForAudioApiByDefault = 0x162;  // bool
        inline constexpr uintptr_t ListenerCFrame = 0x108;  // CoordinateFrame
        inline constexpr uintptr_t ListenerObject = 0xd0;
        inline constexpr uintptr_t ListenerType = 0x154;
        inline constexpr uintptr_t OcclusionEnabled = 0x163;  // bool
        inline constexpr uintptr_t RespectFilteringEnabled = 0x164;  // bool
        inline constexpr uintptr_t ReverbEnabled = 0x165;  // bool
        inline constexpr uintptr_t RolloffScale = 0x158;  // float
        inline constexpr uintptr_t VolumetricAudio = 0x15c;
    }
    namespace Soundscape_TremoloSoundEffect {
        inline constexpr uintptr_t Depth = 0xe0;  // float
        inline constexpr uintptr_t Duty = 0xe4;  // float
        inline constexpr uintptr_t Frequency = 0xe8;  // float
    }
    namespace Sparkles {
        inline constexpr uintptr_t Enabled = 0xb4;  // bool
        inline constexpr uintptr_t LocalTransparencyModifier = 0xac;  // float
        inline constexpr uintptr_t SparkleColor = 0xa0;  // Color3
        inline constexpr uintptr_t TimeScale = 0xb0;  // float
    }
    namespace SpawnLocation {
        inline constexpr uintptr_t AllowTeamChangeOnTouch = 0x1c8;  // bool
        inline constexpr uintptr_t Duration = 0x1c0;  // int
        inline constexpr uintptr_t Enabled = 0x1c9;  // bool
        inline constexpr uintptr_t Neutral = 0x1ca;  // bool
        inline constexpr uintptr_t TeamColor = 0x1c4;  // BrickColor
    }
    namespace SpecialShape {
        inline constexpr uintptr_t MeshType = 0x120;  // Enums::MeshTypeEnum::MeshType
    }
    namespace SphereHandleAdornment {
        inline constexpr uintptr_t DoubleSided = 0x194;  // bool
        inline constexpr uintptr_t Radius = 0x18c;  // float
        inline constexpr uintptr_t Shading = 0x190;  // Enums::AdornShading
    }
    namespace SpotLight {
        inline constexpr uintptr_t Angle = 0xbc;  // float
        inline constexpr uintptr_t Face = 0xc0;  // NormalId
        inline constexpr uintptr_t Range = 0xc4;  // float
    }
    namespace StarterGuiService {
        inline constexpr uintptr_t ClipsDescendantsSupportsRotation = 0x168;  // Enums::RolloutState
        inline constexpr uintptr_t ProcessUserInput = 0x178;  // bool
        inline constexpr uintptr_t ResetPlayerGuiOnSpawn = 0x179;  // bool
        inline constexpr uintptr_t RtlTextSupport = 0x16c;  // Enums::RtlTextSupport
        inline constexpr uintptr_t ScreenOrientation = 0x170;  // Enums::ScreenOrientationEnum::ScreenOrientation
        inline constexpr uintptr_t ShowDevelopmentGui = 0x17a;  // bool
        inline constexpr uintptr_t VirtualCursorMode = 0x174;  // Enums::VirtualCursorMode
    }
    namespace StarterPlayerService {
        inline constexpr uintptr_t AllowCustomAnimations = 0x118;  // bool
        inline constexpr uintptr_t AutoJumpEnabled = 0x119;  // bool
        inline constexpr uintptr_t CameraMaxZoomDistance = 0xc4;  // float
        inline constexpr uintptr_t CameraMinZoomDistance = 0xc8;  // float
        inline constexpr uintptr_t CameraMode = 0xcc;  // Enums::CameraModeEnum::CameraMode
        inline constexpr uintptr_t CharacterBreakJointsOnDeath = 0x11a;  // bool
        inline constexpr uintptr_t CharacterJumpHeight = 0xd0;  // float
        inline constexpr uintptr_t CharacterJumpPower = 0xd4;  // float
        inline constexpr uintptr_t CharacterMaxSlopeAngle = 0xd8;  // float
        inline constexpr uintptr_t CharacterUseJumpPower = 0x11b;  // bool
        inline constexpr uintptr_t CharacterWalkSpeed = 0xdc;  // float
        inline constexpr uintptr_t ClassicDeath = 0x11c;  // bool
        inline constexpr uintptr_t CreateDefaultPlayerModule = 0x11d;  // bool
        inline constexpr uintptr_t DevCameraOcclusionMode = 0xe0;  // Enums::DevCameraOcclusionModeEnum::DeveloperCameraOcclusionMode
        inline constexpr uintptr_t DevComputerCameraMovementMode = 0xe4;  // Enums::DevComputerCameraMovementModeEnum::DeveloperComputerCameraMovementMode
        inline constexpr uintptr_t DevComputerMovementMode = 0xe8;  // Enums::DevComputerMovementModeEnum::DeveloperComputerMovementMode
        inline constexpr uintptr_t DevTouchCameraMovementMode = 0xec;  // Enums::DevTouchCameraMovementModeEnum::DeveloperTouchCameraMovementMode
        inline constexpr uintptr_t DevTouchMovementMode = 0xf0;  // Enums::DevTouchMovementModeEnum::DeveloperTouchMovementMode
        inline constexpr uintptr_t EnableDynamicHeads = 0xf4;  // LoadDynamicHeads
        inline constexpr uintptr_t EnableMouseLockOption = 0x11e;  // bool
        inline constexpr uintptr_t GameSettingsAvatar = 0xf8;  // GameAvatarType
        inline constexpr uintptr_t GameSettingsR15Collision = 0xfc;  // R15CollisionType
        inline constexpr uintptr_t HealthDisplayDistance = 0x100;  // float
        inline constexpr uintptr_t LoadCharacterAppearance = 0x11f;  // bool
        inline constexpr uintptr_t NameDisplayDistance = 0x10c;  // float
        inline constexpr uintptr_t PlayerModuleStatus = 0x110;  // int
        inline constexpr uintptr_t UseImprovedCharacterEvents = 0x114;  // Enums::RolloutState
        inline constexpr uintptr_t UserEmotesEnabled = 0x120;  // bool
    }
    namespace StateMachineDefinition {
        inline constexpr uintptr_t NodeId = 0x98;
    }
    namespace StateMachineTransitionDefinition {
        inline constexpr uintptr_t Priority = 0xd0;  // int
        inline constexpr uintptr_t TransitionId = 0x98;
    }
    namespace StringValue {
        inline constexpr uintptr_t Value = 0xa0;
    }
    namespace StudioData {
        inline constexpr uintptr_t EnableScriptCollabByDefaultOnLoad = 0xb0;  // bool
    }
    namespace Styling_StyleDerive {
        inline constexpr uintptr_t Index = 0xb0;  // int
        inline constexpr uintptr_t Priority = 0xb4;  // int
    }
    namespace Styling_StyleRule {
        inline constexpr uintptr_t Index = 0x140;  // int
        inline constexpr uintptr_t Priority = 0x144;  // int
        inline constexpr uintptr_t Selector = 0x110;
    }
    namespace SunRaysEffect {
        inline constexpr uintptr_t Intensity = 0x98;  // float
        inline constexpr uintptr_t Spread = 0x9c;  // float
    }
    namespace SurfaceAppearance {
        inline constexpr uintptr_t AlphaMode = 0x1a8;  // TexturePackAlphaMode
        inline constexpr uintptr_t Color = 0x190;  // Color3
        inline constexpr uintptr_t ColorMapContent = 0xa0;  // Content
        inline constexpr uintptr_t EmissiveMaskContent = 0xc8;  // Content
        inline constexpr uintptr_t EmissiveStrength = 0x1ac;  // float
        inline constexpr uintptr_t EmissiveTint = 0x19c;  // Color3
        inline constexpr uintptr_t MetalnessMapContent = 0xf0;  // Content
        inline constexpr uintptr_t NormalMapContent = 0x118;  // Content
        inline constexpr uintptr_t ResampleMode = 0x1b0;  // Enums::ImageResampleMode
        inline constexpr uintptr_t RoughnessMapContent = 0x140;  // Content
        inline constexpr uintptr_t SurfaceSlot = 0x1b4;  // int
    }
    namespace SurfaceGui {
        inline constexpr uintptr_t HorizontalCurvature = 0x79c;  // float
        inline constexpr uintptr_t MaxDistance = 0x7a4;  // float
        inline constexpr uintptr_t Shape = 0x7ac;  // SurfaceGuiShape
    }
    namespace SurfaceGuiBase {
        inline constexpr uintptr_t Active = 0x6ac;  // bool
        inline constexpr uintptr_t Face = 0x6a8;  // NormalId
    }
    namespace SurfaceLight {
        inline constexpr uintptr_t Angle = 0xbc;  // float
        inline constexpr uintptr_t Face = 0xc0;  // NormalId
        inline constexpr uintptr_t Range = 0xc4;  // float
    }
    namespace SurfaceSelection {
        inline constexpr uintptr_t TargetSurface = 0xe8;  // NormalId
    }
    namespace SwimController {
        inline constexpr uintptr_t AccelerationTime = 0xc0;  // float
        inline constexpr uintptr_t PitchMaxTorque = 0xc4;  // float
        inline constexpr uintptr_t PitchSpeedFactor = 0xc8;  // float
        inline constexpr uintptr_t RollMaxTorque = 0xcc;  // float
        inline constexpr uintptr_t RollSpeedFactor = 0xd0;  // float
    }
    namespace Team {
        inline constexpr uintptr_t AutoAssignable = 0xa4;  // bool
        inline constexpr uintptr_t AutoColorCharacters = 0xa5;  // bool
        inline constexpr uintptr_t ChildOrder = 0x98;  // int
        inline constexpr uintptr_t Score = 0x9c;  // int
        inline constexpr uintptr_t TeamColor = 0xa0;  // BrickColor
    }
    namespace TeleportOptions {
        inline constexpr uintptr_t ReservedServerAccessCode = 0x98;
        inline constexpr uintptr_t ReservedServerId = 0xb0;
        inline constexpr uintptr_t ServerInstanceId = 0xc8;
        inline constexpr uintptr_t ShouldReserveServer = 0xf8;  // bool
        inline constexpr uintptr_t VipServerId = 0xe0;
    }
    namespace TeleportService {
        inline constexpr uintptr_t CustomizedTeleportUI = 0xb0;  // bool
    }
    namespace TerrainDetail {
        inline constexpr uintptr_t ColorMapContent = 0xa0;  // Content
        inline constexpr uintptr_t EmissiveMaskContent = 0xc8;  // Content
        inline constexpr uintptr_t EmissiveStrength = 0x19c;  // float
        inline constexpr uintptr_t EmissiveTint = 0x190;  // Color3
        inline constexpr uintptr_t Face = 0x1a0;  // TerrainFace
        inline constexpr uintptr_t MaterialPattern = 0x1a4;  // MaterialPattern
        inline constexpr uintptr_t MetalnessMapContent = 0xf0;  // Content
        inline constexpr uintptr_t NormalMapContent = 0x118;  // Content
        inline constexpr uintptr_t RoughnessMapContent = 0x140;  // Content
        inline constexpr uintptr_t StudsPerTile = 0x1a8;  // float
    }
    namespace TestService {
        inline constexpr uintptr_t AutoRuns = 0xe8;  // bool
        inline constexpr uintptr_t Description = 0xa8;
        inline constexpr uintptr_t ExecuteWithStudioRun = 0xe9;  // bool
        inline constexpr uintptr_t Is30FpsThrottleEnabled = 0xec;  // bool
        inline constexpr uintptr_t IsPhysicsEnvironmentalThrottled = 0xea;  // bool
        inline constexpr uintptr_t IsSleepAllowed = 0xeb;  // bool
        inline constexpr uintptr_t NumberOfPlayers = 0xdc;  // int
        inline constexpr uintptr_t SimulateSecondsLag = 0xc8;  // double
        inline constexpr uintptr_t ThrottlePhysicsToRealtime = 0xec;  // bool
        inline constexpr uintptr_t Timeout = 0xd0;  // double
    }
    namespace Text_GetTextBoundsParams {
        inline constexpr uintptr_t Font = 0xb8;
        inline constexpr uintptr_t RichText = 0xc8;  // bool
        inline constexpr uintptr_t Size = 0xc0;  // float
        inline constexpr uintptr_t Text = 0xa0;
        inline constexpr uintptr_t Width = 0xc4;  // float
    }
    namespace TextBox {
        inline constexpr uintptr_t Confidential = 0xed9;  // bool
        inline constexpr uintptr_t LocalizationMatchIdentifier = 0xdf8;
        inline constexpr uintptr_t LocalizationMatchedSourceText = 0xe10;
        inline constexpr uintptr_t ManualFocusRelease = 0xedb;  // bool
        inline constexpr uintptr_t OverlayNativeInput = 0xedd;  // bool
        inline constexpr uintptr_t ReturnKeyType = 0xeb0;  // Enums::ReturnKeyTypeEnum::ReturnKeyType
        inline constexpr uintptr_t ShouldEmitReturnEvents = 0xedf;  // bool
        inline constexpr uintptr_t ShouldEmitTabEvents = 0xee0;  // bool
        inline constexpr uintptr_t ShouldEmitUpAndDownArrowEvents = 0xee1;  // bool
        inline constexpr uintptr_t TextInputType = 0xebc;  // Enums::TextInputTypeEnum::TextInputType
    }
    namespace TextChannel {
        inline constexpr uintptr_t AddPlayersOnJoin = 0xa8;  // bool
        inline constexpr uintptr_t IsDefaultTextChannel = 0xa9;  // bool
    }
    namespace TextChannelWindow {
        inline constexpr uintptr_t Target = 0x9a0;
        inline constexpr uintptr_t UseDefaultFont = 0x9b9;  // bool
    }
    namespace TextChatCommand {
        inline constexpr uintptr_t AutocompleteVisible = 0xc8;  // bool
        inline constexpr uintptr_t Enabled = 0xc9;  // bool
        inline constexpr uintptr_t PrimaryAlias = 0x98;
        inline constexpr uintptr_t SecondaryAlias = 0xb0;
    }
    namespace TextChatMessage {
        inline constexpr uintptr_t BubbleChatMessageProperties = 0x1f0;
        inline constexpr uintptr_t ChatActionType = 0xa0;
        inline constexpr uintptr_t ChatWindowMessageProperties = 0x200;
        inline constexpr uintptr_t ForModeration = 0x244;  // bool
        inline constexpr uintptr_t IsHiddenMessage = 0x245;  // bool
        inline constexpr uintptr_t IsHistorical = 0x246;  // bool
        inline constexpr uintptr_t MessageId = 0xb8;
        inline constexpr uintptr_t Metadata = 0xd0;
        inline constexpr uintptr_t OriginalText = 0xe8;
        inline constexpr uintptr_t PrefixTextInternal = 0x118;
        inline constexpr uintptr_t PresetChatVersion = 0x130;
        inline constexpr uintptr_t PresetId = 0x148;
        inline constexpr uintptr_t RewrittenText = 0x160;
        inline constexpr uintptr_t RewrittenTranslation = 0x178;
        inline constexpr uintptr_t TextChannel = 0x210;
        inline constexpr uintptr_t TextInternal = 0x1a8;
        inline constexpr uintptr_t TextSource = 0x220;
        inline constexpr uintptr_t TranslationInternal = 0x1d8;
        inline constexpr uintptr_t Verified = 0x247;  // bool
        inline constexpr uintptr_t WasRewritten = 0x248;  // bool
    }
    namespace TextChatService {
        inline constexpr uintptr_t ChatVersion = 0x1e0;  // Enums::ChatVersion
        inline constexpr uintptr_t CreateDefaultCommands = 0x1eb;  // bool
        inline constexpr uintptr_t CreateDefaultTextChannels = 0x1ec;  // bool
        inline constexpr uintptr_t HasSeenDeprecationDialog = 0x1ed;  // bool
        inline constexpr uintptr_t IsLegacyChatDisabled = 0x1ee;  // bool
        inline constexpr uintptr_t PlatformIntegratedChat = 0x1e4;  // Enums::RolloutState
    }
    namespace TextGenerator {
        inline constexpr uintptr_t Seed = 0xb0;  // int
        inline constexpr uintptr_t SystemPrompt = 0x98;
        inline constexpr uintptr_t Temperature = 0xb4;  // float
        inline constexpr uintptr_t TopP = 0xb8;  // float
    }
    namespace TextLabel {
        inline constexpr uintptr_t Confidential = 0xea4;  // bool
        inline constexpr uintptr_t LocalizationMatchIdentifier = 0xdf8;
        inline constexpr uintptr_t LocalizationMatchedSourceText = 0xe10;
    }
    namespace TextSource {
        inline constexpr uintptr_t CanSend = 0xd0;  // bool
        inline constexpr uintptr_t DisplayName = 0x98;
        inline constexpr uintptr_t Username = 0xb0;
    }
    namespace Tool {
        inline constexpr uintptr_t CanBeDropped = 0x430;  // bool
        inline constexpr uintptr_t Enabled = 0x431;  // bool
        inline constexpr uintptr_t Grip = 0x400;  // CoordinateFrame
        inline constexpr uintptr_t GripForward = 0x408;  // Vector3
        inline constexpr uintptr_t GripPos = 0x424;  // Vector3
        inline constexpr uintptr_t GripRight = 0x400;  // Vector3
        inline constexpr uintptr_t GripUp = 0x404;  // Vector3
        inline constexpr uintptr_t ManualActivationOnly = 0x432;  // bool
        inline constexpr uintptr_t RequiresHandle = 0x433;  // bool
        inline constexpr uintptr_t ToolTip = 0x3e8;
    }
    namespace Trail {
        inline constexpr uintptr_t Brightness = 0x1a0;  // float
        inline constexpr uintptr_t Color = 0x120;  // ColorSequence
        inline constexpr uintptr_t Enabled = 0x1c4;  // bool
        inline constexpr uintptr_t FaceCamera = 0x1c5;  // bool
        inline constexpr uintptr_t Lifetime = 0x1a4;  // float
        inline constexpr uintptr_t LightEmission = 0x1a8;  // float
        inline constexpr uintptr_t LightInfluence = 0x1ac;  // float
        inline constexpr uintptr_t LocalTransparencyModifier = 0x1b0;  // float
        inline constexpr uintptr_t MaxLength = 0x1b4;  // float
        inline constexpr uintptr_t MinLength = 0x1b8;  // float
        inline constexpr uintptr_t TextureLength = 0x1bc;  // float
        inline constexpr uintptr_t TextureMode = 0x1c0;  // TextureMode
        inline constexpr uintptr_t Transparency = 0xa0;  // NumberSequence
        inline constexpr uintptr_t WidthScale = 0xe0;  // NumberSequence
    }
    namespace TriangleMeshPart {
        inline constexpr uintptr_t InertiaMigrated = 0x238;  // bool
        inline constexpr uintptr_t PCDRequestId = 0x230;  // int
        inline constexpr uintptr_t UnscaledCofm = 0x20c;  // Vector3
        inline constexpr uintptr_t UnscaledVolInertiaDiags = 0x218;  // Vector3
        inline constexpr uintptr_t UnscaledVolInertiaOffDiags = 0x224;  // Vector3
        inline constexpr uintptr_t UnscaledVolume = 0x234;  // float
    }
    namespace UIDragDetector {
        inline constexpr uintptr_t BoundingBehavior = 0x178;  // UIDragDetectorBoundingBehavior
        inline constexpr uintptr_t BoundingUI = 0xf8;
        inline constexpr uintptr_t DragAxis = 0x170;  // Vector2
        inline constexpr uintptr_t DragRelativity = 0x17c;  // UIDragDetectorDragRelativity
        inline constexpr uintptr_t DragRotation = 0x180;  // float
        inline constexpr uintptr_t DragSpace = 0x184;  // UIDragDetectorDragSpace
        inline constexpr uintptr_t DragStyle = 0x188;  // UIDragDetectorDragStyle
        inline constexpr uintptr_t DragUDim2 = 0x130;  // UDim2
        inline constexpr uintptr_t Enabled = 0x1a0;  // bool
        inline constexpr uintptr_t MaxDragAngle = 0x18c;  // float
        inline constexpr uintptr_t MaxDragTranslation = 0x140;  // UDim2
        inline constexpr uintptr_t MinDragAngle = 0x190;  // float
        inline constexpr uintptr_t MinDragTranslation = 0x150;  // UDim2
        inline constexpr uintptr_t ReferenceUIInstance = 0x108;
        inline constexpr uintptr_t ResponseStyle = 0x194;  // UIDragDetectorResponseStyle
        inline constexpr uintptr_t Selectable = 0x1a1;  // bool
        inline constexpr uintptr_t SelectionModeDragSpeed = 0x160;  // UDim2
        inline constexpr uintptr_t SelectionModeRotateSpeed = 0x198;  // float
        inline constexpr uintptr_t UIDragSpeedAxisMapping = 0x19c;  // Enums::UIDragSpeedAxisMapping
    }
    namespace UIPageLayout {
        inline constexpr uintptr_t Animated = 0x154;  // bool
        inline constexpr uintptr_t Circular = 0x155;  // bool
        inline constexpr uintptr_t EasingDirection = 0x148;  // Enums::EasingDirection
        inline constexpr uintptr_t EasingStyle = 0x14c;  // Enums::EasingStyle
        inline constexpr uintptr_t GamepadInputEnabled = 0x156;  // bool
        inline constexpr uintptr_t Padding = 0x140;  // UDim
        inline constexpr uintptr_t ScrollWheelInputEnabled = 0x157;  // bool
        inline constexpr uintptr_t TouchInputEnabled = 0x158;  // bool
        inline constexpr uintptr_t TweenTime = 0x150;  // float
    }
    namespace UITableLayout {
        inline constexpr uintptr_t FillEmptySpaceColumns = 0x14c;  // bool
        inline constexpr uintptr_t FillEmptySpaceRows = 0x14d;  // bool
        inline constexpr uintptr_t MajorAxis = 0x148;  // Enums::TableMajorAxisEnum::TableMajorAxis
        inline constexpr uintptr_t Padding = 0x138;  // UDim2
    }
    namespace UserInputService {
        inline constexpr uintptr_t LegacyInputEventsEnabled = 0xd8;  // bool
    }
    namespace VRService {
        inline constexpr uintptr_t AutomaticScaling = 0xf8;  // Enums::VRScaling
        inline constexpr uintptr_t AvatarGestures = 0x114;  // bool
        inline constexpr uintptr_t ControllerModels = 0xfc;  // Enums::VRControllerModelMode
        inline constexpr uintptr_t FadeOutViewOnCollision = 0x116;  // bool
        inline constexpr uintptr_t GuiInputUserCFrame = 0x100;  // Enums::UserCFrameEnum::UserCFrame
        inline constexpr uintptr_t LaserPointer = 0x104;  // Enums::VRLaserPointerMode
        inline constexpr uintptr_t QuestASWState = 0x117;  // bool
        inline constexpr uintptr_t QuestDisplayRefreshRate = 0x10c;  // float
    }
    namespace Vector3Value {
        inline constexpr uintptr_t Value = 0xa0;  // Vector3
    }
    namespace VehicleSeat {
        inline constexpr uintptr_t HeadsUpDisplay = 0x215;  // bool
        inline constexpr uintptr_t MaxSpeed = 0x200;  // float
        inline constexpr uintptr_t Steer = 0x204;  // int
        inline constexpr uintptr_t SteerFloat = 0x204;  // float
        inline constexpr uintptr_t Throttle = 0x208;  // int
        inline constexpr uintptr_t ThrottleFloat = 0x208;  // float
        inline constexpr uintptr_t Torque = 0x20c;  // float
        inline constexpr uintptr_t TurnSpeed = 0x210;  // float
    }
    namespace VelocityMotor {
        inline constexpr uintptr_t CurrentAngle = 0xe0;  // float; at *(object + 0x168) + this
        inline constexpr uintptr_t DesiredAngle = 0xf8;  // float; at *(object + 0x168) + this
        inline constexpr uintptr_t Hole = 0x178;
        inline constexpr uintptr_t MaxVelocity = 0xf4;  // float; at *(object + 0x168) + this
    }
    namespace VersionControlService {
        inline constexpr uintptr_t ScriptCollabEnabled = 0x100;  // bool
        inline constexpr uintptr_t ScriptCollabVersionHistoryEnabled = 0x101;  // bool
    }
    namespace VideoCaptureService {
        inline constexpr uintptr_t CameraID = 0xb0;
    }
    namespace VideoDisplay {
        inline constexpr uintptr_t ScaleType = 0xa80;  // Enums::ImageScale
        inline constexpr uintptr_t TileSize = 0xa50;  // UDim2
        inline constexpr uintptr_t VideoColor3 = 0xa60;  // Color3
        inline constexpr uintptr_t VideoRectOffset = 0xa6c;  // Vector2
        inline constexpr uintptr_t VideoRectSize = 0xa74;  // Vector2
        inline constexpr uintptr_t VideoTransparency = 0xa84;  // float
    }
    namespace VideoFrame {
        inline constexpr uintptr_t InternalVideoUsage = 0x9d8;  // VideoUsage
        inline constexpr uintptr_t Looped = 0x9f0;  // bool
        inline constexpr uintptr_t MaximumResolution = 0x9dc;  // VideoSampleSize
        inline constexpr uintptr_t Playing = 0x9f1;  // bool
        inline constexpr uintptr_t PlayingReplicating = 0x9f1;  // bool
        inline constexpr uintptr_t RollOffMaxDistance = 0x9e0;  // float
        inline constexpr uintptr_t RollOffMinDistance = 0x9e4;  // float
        inline constexpr uintptr_t RollOffMode = 0x9e8;  // Soundscape::RollOffMode
        inline constexpr uintptr_t TimePosition = 0x9d0;  // double
        inline constexpr uintptr_t TimePositionReplicating = 0x9d0;  // double
        inline constexpr uintptr_t VideoContent = 0x9a8;  // Content
        inline constexpr uintptr_t Volume = 0x9ec;  // float
    }
    namespace VideoPlayer {
        inline constexpr uintptr_t AutoLoadInStudio = 0x161;  // bool
        inline constexpr uintptr_t AutoPlayInStudio = 0x162;  // bool
        inline constexpr uintptr_t InternalVideoUsage = 0x150;  // VideoUsage
        inline constexpr uintptr_t Looping = 0x164;  // bool
        inline constexpr uintptr_t MaximumResolution = 0x154;  // VideoSampleSize
        inline constexpr uintptr_t PlaybackSpeed = 0x158;  // float
        inline constexpr uintptr_t PlayingReplicating = 0x160;  // bool
        inline constexpr uintptr_t VideoContent = 0x120;  // Content
        inline constexpr uintptr_t Volume = 0x15c;  // float
    }
    namespace ViewportFrame {
        inline constexpr uintptr_t CameraCFrame = 0x9b8;  // CoordinateFrame
        inline constexpr uintptr_t CameraFieldOfView = 0xa18;  // float
        inline constexpr uintptr_t IsMirrored = 0xa20;  // bool
    }
    namespace VirtualInputManager {
        inline constexpr uintptr_t AdditionalLuaState = 0x120;
    }
    namespace VisualizationMode {
        inline constexpr uintptr_t Enabled = 0xc8;  // bool
        inline constexpr uintptr_t Title = 0x98;
        inline constexpr uintptr_t ToolTip = 0xb0;
    }
    namespace VisualizationModeCategory {
        inline constexpr uintptr_t Enabled = 0xb0;  // bool
        inline constexpr uintptr_t Title = 0x98;
    }
    namespace VoiceChatService {
        inline constexpr uintptr_t DefaultDistanceAttenuation = 0x1e0;  // Enums::VoiceChatDistanceAttenuationType
        inline constexpr uintptr_t EnableDefaultVoice = 0x1ec;  // bool
        inline constexpr uintptr_t EnableVoiceVolumeControls = 0x1e4;  // Enums::RolloutState
        inline constexpr uintptr_t UseAudioApi = 0x1e8;  // Enums::AudioApiRollout
        inline constexpr uintptr_t UseNewAudioApi = 0x1ed;  // bool
        inline constexpr uintptr_t UseNewControlPaths = 0x1ee;  // bool
        inline constexpr uintptr_t UseNewJoinFlow = 0x1ef;  // bool
        inline constexpr uintptr_t UseStreamSwitching = 0x1f0;  // bool
        inline constexpr uintptr_t VoiceChatEnabledForPlaceOnRcc = 0x1f1;  // bool
        inline constexpr uintptr_t VoiceChatEnabledForUniverseOnRcc = 0x1f2;  // bool
    }
    namespace Weld {
        inline constexpr uintptr_t EnableSkinning = 0x170;  // bool
    }
    namespace Wire {
        inline constexpr uintptr_t SourceName = 0xa0;
        inline constexpr uintptr_t TargetName = 0xb8;
    }
    namespace WireframeHandleAdornment {
        inline constexpr uintptr_t Scale = 0x18c;  // Vector3
        inline constexpr uintptr_t Thickness = 0x198;  // float
    }
    namespace WorldModel {
        inline constexpr uintptr_t UseWorkspaceCollisionGroups = 0x428;  // bool
    }
    namespace WorldRoot {
        inline constexpr uintptr_t AutoSimulate = 0x324;  // bool
        inline constexpr uintptr_t GravityDirection = 0x300;  // Vector3
        inline constexpr uintptr_t SimulationRate = 0x31c;  // float
        inline constexpr uintptr_t Wind = 0x320;  // float
        inline constexpr uintptr_t WindDirection = 0x30c;  // Vector3
    }
    namespace WrapLayer {
        inline constexpr uintptr_t AutoSkin = 0x3a4;  // WrapLayerAutoSkin
        inline constexpr uintptr_t BindOffset = 0x320;  // CoordinateFrame
        inline constexpr uintptr_t Color = 0x380;  // Color3
        inline constexpr uintptr_t DebugMode = 0x3a8;  // WrapLayerDebugMode
        inline constexpr uintptr_t Enabled = 0x3bc;  // bool
        inline constexpr uintptr_t MaxSize = 0x38c;  // Vector3
        inline constexpr uintptr_t Offset = 0x398;  // Vector3
        inline constexpr uintptr_t Order = 0x3ac;  // int
        inline constexpr uintptr_t Puffiness = 0x3b0;  // float
        inline constexpr uintptr_t ReferenceMeshContent = 0x280;  // Content
        inline constexpr uintptr_t ReferenceOrigin = 0x350;  // CoordinateFrame
        inline constexpr uintptr_t RotateScaleDeformationMap = 0x2a8;  // Content
        inline constexpr uintptr_t ScaleOnlyDeformationMap = 0x2d0;  // Content
        inline constexpr uintptr_t ShrinkFactor = 0x3b4;  // float
        inline constexpr uintptr_t TargetShaping = 0x3b8;  // float
    }
    namespace WrapTarget {
        inline constexpr uintptr_t Color = 0x280;  // Color3
        inline constexpr uintptr_t DebugMode = 0x28c;  // WrapTargetDebugMode
        inline constexpr uintptr_t Stiffness = 0x290;  // float
    }
    namespace WrapTextureTransfer {
        inline constexpr uintptr_t UVMaxBound = 0xc0;  // Vector2
        inline constexpr uintptr_t UVMinBound = 0xc8;  // Vector2
    }
}
