// WeirdExt offsets — macOS ARM64
//
// Roblox Version  : 0.745.0.7451137
// Binary SHA-256  : 8af3f95d347a5283618dd9c17f4a1b02b59982ff699f00cc6f2a195377f2f6b7
// Dumped At       : 2026-11-15 03:04 UTC
// Total Offsets   : 2338 (37 confirmed live, 2301 from reflection)
//
// macOS layouts differ from Windows; use these with the macOS client only.

namespace Offsets
{
    public static class Instance
    {
        public const long Name = 0x68;  // pointer to std::string
        public const long Parent = 0x60;
        public const long ChildrenStart = 0x70;  // pointer to a vector of 16-byte smart pointers
        public const long ChildrenEnd = 0x8;  // end pointer, relative to the children vector
        public const long This = 0x8;  // (self, control block) smart pointer pair
        public const long numExpectedDirectChildren = 0x80;  // int
    }
    public static class Players
    {
        public const long LocalPlayer = 0x108;
        public const long BanningEnabled = 0x124;  // bool
        public const long CharacterAutoLoads = 0x125;  // bool
        public const long MaxPlayersInternal = 0x118;  // int
        public const long PreferredPlayersInternal = 0x11c;  // int
        public const long RespawnTime = 0x120;  // float
        public const long ServerGitHash = 0xa8;
        public const long ServerLogPrefix = 0xc0;
        public const long UseStrafingAnimations = 0x126;  // bool
    }
    public static class Player
    {
        public const long ModelInstance = 0x258;
        public const long Team = 0x298;
        public const long UserId = 0xb8;  // int64; a second copy sits at 0x2d0
        public const long AccountAgeReplicate = 0x31c;  // int
        public const long AgeChecked = 0x320;  // Enums::AgeCheckStatus
        public const long AutoJumpEnabled = 0x381;  // bool
        public const long CameraFieldOfView = 0x324;  // float
        public const long CameraFrustumRequested = 0x382;  // bool
        public const long CameraMaxZoomDistance = 0x328;  // float
        public const long CameraMinZoomDistance = 0x32c;  // float
        public const long CameraMode = 0x330;  // Enums::CameraModeEnum::CameraMode
        public const long CameraViewportSize = 0x314;  // Vector2
        public const long CanLoadCharacterAppearance = 0x383;  // bool
        public const long CharacterAppearance = 0xc0;
        public const long CharacterAppearanceId = 0x2c0;  // int64
        public const long ChatAvailabilityStatus = 0xd8;
        public const long ChatPrivacyMode = 0x334;  // Enums::ChatPrivacyModeEnum::ChatPrivacyMode
        public const long CloudEditCameraCoordinateFrame = 0x2d8;  // CoordinateFrame
        public const long CloudEditPlayerActive = 0x384;  // bool
        public const long CountryRegionCodeReplicate = 0xf0;
        public const long DataComplexityLimit = 0x338;  // int
        public const long DevCameraOcclusionMode = 0x33c;  // Enums::DevCameraOcclusionModeEnum::DeveloperCameraOcclusionMode
        public const long DevComputerCameraMode = 0x340;  // Enums::DevComputerCameraMovementModeEnum::DeveloperComputerCameraMovementMode
        public const long DevComputerMovementMode = 0x344;  // Enums::DevComputerMovementModeEnum::DeveloperComputerMovementMode
        public const long DevEnableMouseLock = 0x386;  // bool
        public const long DevTouchCameraMode = 0x348;  // Enums::DevTouchCameraMovementModeEnum::DeveloperTouchCameraMovementMode
        public const long DevTouchMovementMode = 0x34c;  // Enums::DevTouchMovementModeEnum::DeveloperTouchMovementMode
        public const long DisplayName = 0x108;
        public const long FollowUserIdReplicated = 0x2c8;  // int64
        public const long FrustumStreaming = 0x354;  // Enums::FrustumStreamingMode
        public const long GameplayPaused = 0x387;  // bool
        public const long HasRobloxSubscription = 0x388;  // bool
        public const long HasVerifiedBadge = 0x389;  // bool
        public const long HealthDisplayDistance = 0x358;  // float
        public const long InputLatency = 0x35c;  // int
        public const long InternalCharacterAppearanceLoaded = 0x38a;  // bool
        public const long MaximumSimulationRadius = 0x360;  // float
        public const long MembershipTypeReplicate = 0x364;  // MembershipType
        public const long NameDisplayDistance = 0x368;  // float
        public const long NeedRegionalFallback = 0x38b;  // bool
        public const long Neutral = 0x38c;  // bool
        public const long OsPlatform = 0x120;
        public const long PartyId = 0x138;
        public const long PlatformName = 0x150;
        public const long RawJoinData = 0x168;  // BinaryString
        public const long SimulationRadius = 0x36c;  // float
        public const long TeamColor = 0x370;  // BrickColor
        public const long TeleportedIn = 0x38e;  // bool
        public const long UserIdModeReplicate = 0x378;  // UserIdMode
        public const long VRDevice = 0x180;
        public const long VREnabled = 0x390;  // bool
        public const long VoiceChatVolume = 0x37c;  // float
    }
    public static class Workspace
    {
        public const long CurrentCamera = 0x458;
        public const long AirTurbulenceIntensity = 0x490;  // float
        public const long AllowThirdPartySales = 0x538;  // bool
        public const long AuthorityMode = 0x494;  // Enums::AuthorityMode
        public const long AvatarUnificationMode = 0x498;  // Enums::AvatarUnificationMode
        public const long ClientAnimatorThrottling = 0x49c;  // Enums::ClientAnimatorThrottlingMode
        public const long DistributedGameTime = 0x478;  // double
        public const long EnableSLIMAvatars = 0x4a0;  // Enums::RolloutState
        public const long ExpandedTerrain = 0x4a4;  // Enums::RolloutState
        public const long FallHeightEnabled = 0x53a;  // bool
        public const long FluidForces = 0x4a8;  // Enums::FluidForceModelMode
        public const long IKControlConstraintSupport = 0x4ac;  // Enums::IkControlConstraintSupport
        public const long ImprovedAnimationConstraint = 0x4b0;  // Enums::RolloutState
        public const long ImprovedPhysicsReplication = 0x4b4;  // Enums::RolloutState
        public const long InsertPoint = 0x578;  // Vector3
        public const long InterpolationThrottling = 0x4b8;  // Enums::InterpolationThrottlingMode
        public const long LayeredClothingCacheOptimizations = 0x4bc;  // Enums::RolloutState
        public const long LuauTypeCheckMode = 0x4c0;  // Enums::LuauTypeCheckMode
        public const long MapTVRemoteToGamepadKeycodes = 0x4c4;  // Enums::RolloutState
        public const long MeshPartHeadsAndAccessories = 0x4c8;  // Enums::MeshPartHeadsAndAccessories
        public const long MeshStreamingAndImprovedLods = 0x4cc;  // Enums::RolloutState
        public const long ModelStreamingBehavior = 0x4d0;  // Enums::ModelStreamingBehavior
        public const long PathfindingUseImprovedSearch = 0x4d8;  // Enums::PathfindingUseImprovedSearch
        public const long PhysicsSteppingMethod = 0x4dc;  // Enums::PhysicsSteppingMethod
        public const long PlayerCharacterDestroyBehavior = 0x4e0;  // Enums::PlayerCharacterDestroyBehavior
        public const long PredictiveStreamingMode = 0x4e8;  // Enums::PredictiveStreamingMode
        public const long PrimalPhysicsSolver = 0x4ec;  // Enums::PrimalPhysicsSolverMode
        public const long RejectCharacterDeletions = 0x4f0;  // RejectCharacterDeletions
        public const long RenderingCacheOptimizations = 0x4f4;  // Enums::RenderingCacheOptimizationMode
        public const long ReplicateInstanceDestroySetting = 0x4f8;  // Enums::ReplicateInstanceDestroySetting
        public const long ReplicationFrequency = 0x4fc;  // Enums::ReplicationMode
        public const long ReplicationThroughput = 0x500;  // Enums::ReplicationMode
        public const long Retargeting = 0x504;  // Enums::AnimatorRetargetingMode
        public const long SandboxedInstanceMode = 0x508;  // Enums::SandboxedInstanceMode
        public const long StreamOutBehavior = 0x510;  // Enums::StreamOutBehavior
        public const long StreamingAdaptiveRadius = 0x53b;  // bool
        public const long StreamingEnabledStorage = 0x53c;  // bool
        public const long StreamingIntegrityMode = 0x514;  // Enums::StreamingIntegrityMode
        public const long StreamingMinRadius = 0x518;  // int
        public const long StreamingPauseMode = 0x514;  // Enums::StreamingPauseMode
        public const long StreamingTargetRadius = 0x51c;  // int
        public const long ThrottleLevel = 0x520;  // int
        public const long TouchEventsUseCollisionGroups = 0x524;  // Enums::RolloutState
        public const long UseInputSink = 0x52c;  // Enums::RolloutState
        public const long UseNewLuauTypeSolver = 0x530;  // Enums::RolloutState
        public const long ValidateEnabledProximityPrompt = 0x534;  // Enums::RolloutState
        public const long WatermarkHash = 0x430;
    }
    public static class Camera
    {
        public const long Rotation = 0xb8;  // nine floats, row-major; Position follows at +36
        public const long Position = 0xdc;
        public const long FieldOfView = 0x120;  // float, radians (vertical)
        public const long CameraSubject = 0xa8;  // (object, control block) smart pointer pair
        public const long CFrame = 0xb8;  // CoordinateFrame
        public const long CameraType = 0x118;  // Enums::CameraTypeEnum::CameraType
        public const long DiagonalFieldOfView = 0x11c;  // float
        public const long FieldOfViewMode = 0x124;  // Enums::FieldOfViewMode
        public const long Focus = 0xe8;  // CoordinateFrame
        public const long HeadLocked = 0x144;  // bool
        public const long HeadScale = 0x128;  // float
        public const long MaxAxisFieldOfView = 0x12c;  // float
        public const long OrthographicMode = 0x134;  // Enums::OrthographicMode
        public const long OrthographicSize = 0x138;  // float
        public const long ProjectionType = 0x13c;  // Enums::ProjectionType
        public const long VRTiltAndRollEnabled = 0x145;  // bool
        public const long ViewStretch = 0x140;  // float
    }
    public static class BasePart
    {
        public const long Primitive = 0x168;
        public const long AudioCanCollide = 0x117;  // bool
        public const long CastShadow = 0x118;  // bool
        public const long Elasticity = 0x260;  // float; at *(object + 0x168) + this
        public const long Friction = 0x25c;  // float; at *(object + 0x168) + this
        public const long LocalTransparencyModifier = 0xe8;  // float
        public const long Locked = 0x119;  // bool
        public const long Massless = 0x11a;  // bool
        public const long Material = 0x24e;  // MaterialType; at *(object + 0x168) + this
        public const long NetworkOwnershipRule = 0x26a;  // NetworkOwnership; at *(object + 0x168) + this
        public const long Position = 0xa8;  // Vector3; heuristic decode, passed live check
        public const long Reflectance = 0xec;  // float
        public const long RotVelocity = 0xa8;  // Vector3; heuristic decode, passed live check
        public const long Size = 0x1c4;  // Vector3; at *(object + 0x168) + this
        public const long Transparency = 0x110;  // float
        public const long Velocity = 0xa8;  // Vector3; heuristic decode, passed live check
        public const long size = 0x1c4;  // Vector3; at *(object + 0x168) + this
    }
    public static class Primitive
    {
        public const long Rotation = 0xb0;  // nine floats, row-major; Position follows at +36
        public const long Position = 0xd4;
        public const long Flags = 0x1be;
        public const long AssemblyLinearVelocity = 0xe0;  // copy refreshed from the solver body each physics step
    }
    public static class DataModel
    {
        public const long PlaceId = 0x170;  // int64
        public const long GameId = 0x168;  // int64 (universe id)
        public const long CreatorId = 0x160;  // int64
        public const long JobId = 0x108;  // std::string
        public const long ForceR15 = 0x190;  // bool
    }
    public static class TaskScheduler_Job
    {
        public const long Name = 0x18;  // std::string; empty for some jobs
        public const long DataModel = 0x30;  // pointer; add DataModelInstanceDelta to reach the DataModel Instance
        public const long DataModelInstanceDelta = 0x1e8;  // byte delta, not a field offset
    }
    public static class Humanoid
    {
        public const long Health = 0x174;
        public const long MaxHealth = 0x18c;
        public const long WalkSpeed = 0x1b4;
        public const long WalkSpeedCheck = 0x38c;  // must equal WalkSpeed
        public const long JumpPower = 0x188;
        public const long UseJumpPower = 0x1c6;  // bool
        public const long AutoJumpEnabled = 0x1b8;  // bool
        public const long AutoRotate = 0x1b9;  // bool
        public const long AutomaticScalingEnabled = 0x1ba;  // bool
        public const long BodyPartsCollidableOnDeath = 0x1bb;  // bool
        public const long BreakJointsOnDeath = 0x1bc;  // bool
        public const long CameraOffset = 0x100;  // Vector3
        public const long CollisionType = 0x160;  // Enums::HumanoidCollisionTypeEnum::CollisionType
        public const long DisplayDistanceType = 0x164;  // Enums::HumanoidDisplayDistanceTypeEnum::HumanoidDisplayDistanceType
        public const long DisplayName = 0xa0;
        public const long EvaluateStateMachine = 0x1bd;  // bool
        public const long FinishedState = 0x1be;  // bool
        public const long HealthDisplayDistance = 0x16c;  // float
        public const long HealthDisplayType = 0x170;  // Enums::HumanoidHealthDisplayTypeEnum::HumanoidHealthDisplayType
        public const long Health_XML = 0x174;  // float
        public const long HipHeight = 0x178;  // float
        public const long InternalAvatarRulesRootPartSize = 0x10c;  // Vector3
        public const long InternalAvatarRulesRootPartSizeScalesWithBody = 0x1bf;  // bool
        public const long InternalBodyScale = 0x118;  // Vector3
        public const long InternalDisplayName = 0xb8;
        public const long InternalHeadScale = 0x17c;  // float
        public const long InternalOriginalHipHeight = 0x180;  // float
        public const long Jump = 0x1c0;  // bool
        public const long JumpHeight = 0x184;  // float
        public const long JumpReplicate = 0x1c0;  // bool
        public const long MaxSlopeAngle = 0x190;  // float
        public const long MoveDirectionInternal = 0x124;  // Vector3
        public const long NameDisplayDistance = 0x194;  // float
        public const long NameOcclusion = 0x198;  // Enums::NameOcclusionEnum::NameOcclusion
        public const long NetworkHumanoidState = 0x19c;  // HUMAN::StateType
        public const long NoFloorTimerState = 0x1a0;  // float
        public const long OverrideDefaultCollisions = 0x1c1;  // bool
        public const long PlatformStand = 0x1c2;  // bool
        public const long RequiresNeck = 0x1c3;  // bool
        public const long RigType = 0x1a4;  // HumanoidRigType
        public const long RotationType = 0x1a8;  // Enums::RotationTypeEnum::RotationType
        public const long Sit = 0x1c4;  // bool
        public const long Strafe = 0x1c5;  // bool
        public const long TargetPoint = 0x130;  // Vector3
        public const long TimerState = 0x1ac;  // float
        public const long WalkAngleError = 0x1b0;  // float
        public const long WalkDirection = 0x13c;  // Vector3
        public const long WalkToPart = 0xf0;
        public const long WalkToPoint = 0x148;  // Vector3
        public const long maxHealth = 0x18c;  // float
    }
    public static class PrimitiveFlags
    {
        public const long CanCollide = 0x8;  // bit mask in Primitive::Flags (a byte)
    }
    public static class SolverBody
    {
        public const long Pointer = 0x140;  // Primitive -> solver body that physics integrates
        public const long Position = 0x98;  // Vector3; copies follow every BlockStride bytes
        public const long Velocity = 0xa4;  // Vector3; write here to change motion mid-air
        public const long BlockStride = 0x48;  // bytes between (position, velocity) copies
    }
    public static class Accessory
    {
        public const long AccessoryType = 0x158;  // AccessoryType
    }
    public static class AccessoryDescription
    {
        public const long AccessoryType = 0xd4;  // AccessoryType
        public const long AssetId = 0xa8;  // int64
        public const long Instance = 0x98;
        public const long IsLayered = 0xe0;  // bool
        public const long Order = 0xd8;  // int
        public const long Position = 0xb0;  // Vector3
        public const long Puffiness = 0xdc;  // float
        public const long Rotation = 0xbc;  // Vector3
        public const long Scale = 0xc8;  // Vector3
    }
    public static class Accoutrement
    {
        public const long AttachmentForward = 0xa8;  // Vector3
        public const long AttachmentPoint = 0xa0;  // CoordinateFrame
        public const long AttachmentPos = 0xc4;  // Vector3
        public const long AttachmentRight = 0xa0;  // Vector3
        public const long AttachmentUp = 0xa4;  // Vector3
        public const long BackendAccoutrementState = 0xd0;  // int
    }
    public static class Ads_AdGui
    {
        public const long AdShape = 0x7c0;
        public const long EnableVideoAds = 0x7c4;  // bool
    }
    public static class Ads_AdPlacement
    {
        public const long AdFormat = 0x108;
        public const long PlacementId = 0x100;  // int64
    }
    public static class AirController
    {
        public const long BalanceMaxTorque = 0xcc;  // float
        public const long BalanceSpeed = 0xd0;  // float
        public const long LinearImpulse = 0xc0;  // Vector3
        public const long MaintainAngularMomentum = 0xe0;  // bool
        public const long MaintainLinearMomentum = 0xe1;  // bool
        public const long MoveMaxForce = 0xd4;  // float
        public const long TurnMaxTorque = 0xd8;  // float
        public const long TurnSpeedFactor = 0xdc;  // float
    }
    public static class AnalyticsService
    {
        public const long ApiKey = 0xb0;
    }
    public static class AnimationClip
    {
        public const long Loop = 0xb4;  // bool
        public const long Priority = 0xa0;  // AnimationPriority
    }
    public static class AnimationNodeDefinition
    {
        public const long NodeId = 0x98;
        public const long NodeType = 0xb8;  // Enums::AnimationNodeType
    }
    public static class AnimationPlayer
    {
        public const long AutoPlay = 0xf8;  // bool
        public const long CurrentFrame = 0xf0;  // int
        public const long Enabled = 0xf9;  // bool
        public const long Loop = 0xfb;  // bool
        public const long Speed = 0xf4;  // float
        public const long TimePosition = 0xe8;  // double
        public const long Track = 0xc0;
    }
    public static class AnimationTrack
    {
        public const long TimePosition = 0xc0;  // float
    }
    public static class AnimationValueNodeDefinition
    {
        public const long NodeId = 0x98;
        public const long NodeType = 0xb0;  // Enums::AnimationValueNodeType
    }
    public static class Animator
    {
        public const long AnimTrackMetadata0 = 0x38c;  // AnimTrackMetadata
        public const long AnimTrackMetadata1 = 0x390;  // AnimTrackMetadata
        public const long AnimTrackMetadata10 = 0x394;  // AnimTrackMetadata
        public const long AnimTrackMetadata11 = 0x398;  // AnimTrackMetadata
        public const long AnimTrackMetadata12 = 0x39c;  // AnimTrackMetadata
        public const long AnimTrackMetadata13 = 0x3a0;  // AnimTrackMetadata
        public const long AnimTrackMetadata14 = 0x3a4;  // AnimTrackMetadata
        public const long AnimTrackMetadata15 = 0x3a8;  // AnimTrackMetadata
        public const long AnimTrackMetadata2 = 0x3ac;  // AnimTrackMetadata
        public const long AnimTrackMetadata3 = 0x3b0;  // AnimTrackMetadata
        public const long AnimTrackMetadata4 = 0x3b4;  // AnimTrackMetadata
        public const long AnimTrackMetadata5 = 0x3b8;  // AnimTrackMetadata
        public const long AnimTrackMetadata6 = 0x3bc;  // AnimTrackMetadata
        public const long AnimTrackMetadata7 = 0x3c0;  // AnimTrackMetadata
        public const long AnimTrackMetadata8 = 0x3c4;  // AnimTrackMetadata
        public const long AnimTrackMetadata9 = 0x3c8;  // AnimTrackMetadata
        public const long AnimTrackPlayState0 = 0xd8;  // AnimTrackPlayState
        public const long AnimTrackPlayState1 = 0xe8;  // AnimTrackPlayState
        public const long AnimTrackPlayState10 = 0xf8;  // AnimTrackPlayState
        public const long AnimTrackPlayState11 = 0x108;  // AnimTrackPlayState
        public const long AnimTrackPlayState12 = 0x118;  // AnimTrackPlayState
        public const long AnimTrackPlayState13 = 0x128;  // AnimTrackPlayState
        public const long AnimTrackPlayState14 = 0x138;  // AnimTrackPlayState
        public const long AnimTrackPlayState15 = 0x148;  // AnimTrackPlayState
        public const long AnimTrackPlayState2 = 0x158;  // AnimTrackPlayState
        public const long AnimTrackPlayState3 = 0x168;  // AnimTrackPlayState
        public const long AnimTrackPlayState4 = 0x178;  // AnimTrackPlayState
        public const long AnimTrackPlayState5 = 0x188;  // AnimTrackPlayState
        public const long AnimTrackPlayState6 = 0x198;  // AnimTrackPlayState
        public const long AnimTrackPlayState7 = 0x1a8;  // AnimTrackPlayState
        public const long AnimTrackPlayState8 = 0x1b8;  // AnimTrackPlayState
        public const long AnimTrackPlayState9 = 0x1c8;  // AnimTrackPlayState
        public const long AnimTrackWeight0 = 0x1d8;  // AnimTrackWeight
        public const long AnimTrackWeight1 = 0x1e8;  // AnimTrackWeight
        public const long AnimTrackWeight10 = 0x1f8;  // AnimTrackWeight
        public const long AnimTrackWeight11 = 0x208;  // AnimTrackWeight
        public const long AnimTrackWeight12 = 0x218;  // AnimTrackWeight
        public const long AnimTrackWeight13 = 0x228;  // AnimTrackWeight
        public const long AnimTrackWeight14 = 0x238;  // AnimTrackWeight
        public const long AnimTrackWeight15 = 0x248;  // AnimTrackWeight
        public const long AnimTrackWeight2 = 0x258;  // AnimTrackWeight
        public const long AnimTrackWeight3 = 0x268;  // AnimTrackWeight
        public const long AnimTrackWeight4 = 0x278;  // AnimTrackWeight
        public const long AnimTrackWeight5 = 0x288;  // AnimTrackWeight
        public const long AnimationId0 = 0x2d8;  // int64
        public const long AnimationId1 = 0x2e0;  // int64
        public const long AnimationId10 = 0x2e8;  // int64
        public const long AnimationId11 = 0x2f0;  // int64
        public const long AnimationId12 = 0x2f8;  // int64
        public const long AnimationId13 = 0x300;  // int64
        public const long AnimationId14 = 0x308;  // int64
        public const long AnimationId15 = 0x310;  // int64
        public const long AnimationId2 = 0x318;  // int64
        public const long AnimationId3 = 0x320;  // int64
        public const long AnimationId4 = 0x328;  // int64
        public const long AnimationId5 = 0x330;  // int64
        public const long AnimationId6 = 0x338;  // int64
        public const long AnimationId7 = 0x340;  // int64
        public const long AnimationId8 = 0x348;  // int64
        public const long AnimationId9 = 0x350;  // int64
        public const long PreferLodEnabled = 0x3cc;  // bool
    }
    public static class ArcHandles
    {
        public const long Axes = 0x104;  // Axes
        public const long MouseButton1DownConnectionCount = 0x108;  // int
        public const long MouseButton1UpConnectionCount = 0x10c;  // int
        public const long MouseDragConnectionCount = 0x110;  // int
        public const long MouseEnterConnectionCount = 0x114;  // int
        public const long MouseLeaveConnectionCount = 0x118;  // int
    }
    public static class AssetDeliveryProxy
    {
        public const long Interface = 0xb0;
        public const long StartServer = 0xcc;  // bool
    }
    public static class AssetPatchSettings
    {
        public const long ContentId = 0x98;
        public const long OutputPath = 0xb0;
        public const long PatchId = 0xc8;
    }
    public static class AssetService
    {
        public const long AllowInsertFreeAssets = 0xa1;  // bool
    }
    public static class Atmosphere
    {
        public const long Color = 0xa0;  // Color3
        public const long Decay = 0xac;  // Color3
        public const long Density = 0xb8;  // float
        public const long Glare = 0xbc;  // float
        public const long Haze = 0xc0;  // float
        public const long Offset = 0xc4;  // float
    }
    public static class Attachment
    {
        public const long Axis = 0xa0;  // Vector3
        public const long Orientation = 0xa8;  // Vector3; heuristic decode, passed live check
        public const long Position = 0xac;  // Vector3
        public const long Rotation = 0xa8;  // Vector3; heuristic decode, passed live check
        public const long SecondaryAxis = 0xb8;  // Vector3
        public const long Visible = 0xc4;  // bool
        public const long WorldAxis = 0xa0;  // Vector3; heuristic decode, passed live check
        public const long WorldPosition = 0xb4;  // Vector3; heuristic decode, passed live check
        public const long WorldSecondaryAxis = 0xb8;  // Vector3; heuristic decode, passed live check
    }
    public static class AudioSearchParams
    {
        public const long Album = 0xa0;
        public const long Artist = 0xb8;
        public const long AudioSubType = 0x118;  // AudioSubType
        public const long AudioSubtype = 0x118;  // AudioSubType
        public const long MaxDuration = 0x11c;  // int
        public const long MaxPageSize = 0x120;  // int
        public const long MinDuration = 0x124;  // int
        public const long SearchKeyword = 0xd0;
        public const long SortType = 0x128;  // AudioSortType
        public const long Tag = 0xe8;
        public const long Title = 0x100;
    }
    public static class AuroraScript
    {
        public const long EnableCulling = 0x120;  // bool
        public const long EnableLOD = 0x121;  // bool
        public const long LODCriticality = 0x118;  // int
        public const long Priority = 0x11c;  // int
    }
    public static class AuroraScriptObject
    {
        public const long FrameId = 0xb8;  // int
        public const long LODLevel = 0xbc;  // int
        public const long MaxFrequency = 0xc0;  // int
        public const long PriorFrameInvoked = 0xc4;  // int
    }
    public static class AuroraService
    {
        public const long BufferFullInputCount = 0xc8;  // int
        public const long HashRoundingPoint = 0xb8;  // double
        public const long IgnoreRotation = 0xdc;  // bool
        public const long InputDropRate = 0xcc;  // float
        public const long LockStepIdOffset = 0xdd;  // bool
        public const long OutOfOrderInputCount = 0xd0;  // int
        public const long RCCHeartbeatFPS = 0xc0;  // double
        public const long RollbackOffset = 0xd4;  // int
        public const long TooOldInputCount = 0xd8;  // int
    }
    public static class AvatarAbilityRules
    {
        public const long CharacterControllerMode = 0x98;  // Enums::AvatarSettingsCharacterControllerMode
        public const long EnableClimbing = 0x9c;  // bool
        public const long EnableCrouching = 0x9d;  // bool
        public const long EnableFallingDown = 0x9e;  // bool
        public const long EnableGettingUp = 0x9f;  // bool
        public const long EnableHolding = 0xa0;  // bool
        public const long EnableJumping = 0xa1;  // bool
        public const long EnableReaching = 0xa2;  // bool
        public const long EnableRunning = 0xa3;  // bool
        public const long EnableSitting = 0xa4;  // bool
        public const long EnableSprinting = 0xa5;  // bool
        public const long EnableSwimming = 0xa6;  // bool
        public const long EnableTurning = 0xa7;  // bool
    }
    public static class AvatarAccessoryRules
    {
        public const long AccessoryMode = 0x124;  // Enums::AvatarSettingsAccessoryMode
        public const long BackAccessoryOverride = 0x98;  // int64
        public const long CustomAccessoryMode = 0x128;  // Enums::AvatarSettingsCustomAccessoryMode
        public const long CustomBackAccessoryEnabled = 0x130;  // bool
        public const long CustomBackAccessoryId = 0xa0;  // int64
        public const long CustomFaceAccessoryEnabled = 0x131;  // bool
        public const long CustomFaceAccessoryId = 0xa8;  // int64
        public const long CustomFrontAccessoryEnabled = 0x132;  // bool
        public const long CustomFrontAccessoryId = 0xb0;  // int64
        public const long CustomHairAccessoryEnabled = 0x133;  // bool
        public const long CustomHairAccessoryId = 0xb8;  // int64
        public const long CustomHeadAccessoryEnabled = 0x134;  // bool
        public const long CustomHeadAccessoryId = 0xc0;  // int64
        public const long CustomNeckAccessoryEnabled = 0x135;  // bool
        public const long CustomNeckAccessoryId = 0xc8;  // int64
        public const long CustomShoulderAccessoryEnabled = 0x136;  // bool
        public const long CustomShoulderAccessoryId = 0xd0;  // int64
        public const long CustomWaistAccessoryEnabled = 0x137;  // bool
        public const long CustomWaistAccessoryId = 0xd8;  // int64
        public const long EnableEmissives = 0x138;  // bool
        public const long EnableSound = 0x139;  // bool
        public const long EnableVFX = 0x13a;  // bool
        public const long FaceAccessoryOverride = 0xe0;  // int64
        public const long FrontAccessoryOverride = 0xe8;  // int64
        public const long HairAccessoryOverride = 0xf0;  // int64
        public const long HeadAccessoryOverride = 0xf8;  // int64
        public const long LimitBounds = 0x118;  // Vector3
        public const long LimitMethod = 0x12c;  // Enums::AvatarSettingsAccessoryLimitMethod
        public const long NeckAccessoryOverride = 0x100;  // int64
        public const long ShoulderAccessoryOverride = 0x108;  // int64
        public const long WaistAccessoryOverride = 0x110;  // int64
    }
    public static class AvatarAnimationRules
    {
        public const long AnimationClipsMode = 0x138;  // Enums::AvatarSettingsAnimationClipsMode
        public const long AnimationPacksMode = 0x13c;  // Enums::AvatarSettingsAnimationPacksMode
        public const long ClimbAnimationOverride = 0x98;  // int64
        public const long CustomClimbAnimationEnabled = 0x140;  // bool
        public const long CustomClimbAnimationId = 0xa0;  // int64
        public const long CustomFallAnimationEnabled = 0x141;  // bool
        public const long CustomFallAnimationId = 0xa8;  // int64
        public const long CustomIdleAlt1AnimationEnabled = 0x142;  // bool
        public const long CustomIdleAlt1AnimationId = 0xb0;  // int64
        public const long CustomIdleAlt2AnimationEnabled = 0x143;  // bool
        public const long CustomIdleAlt2AnimationId = 0xb8;  // int64
        public const long CustomIdleAnimationEnabled = 0x144;  // bool
        public const long CustomIdleAnimationId = 0xc0;  // int64
        public const long CustomJumpAnimationEnabled = 0x145;  // bool
        public const long CustomJumpAnimationId = 0xc8;  // int64
        public const long CustomRunAnimationEnabled = 0x146;  // bool
        public const long CustomRunAnimationId = 0xd0;  // int64
        public const long CustomSwimAnimationEnabled = 0x147;  // bool
        public const long CustomSwimAnimationId = 0xd8;  // int64
        public const long CustomSwimIdleAnimationEnabled = 0x148;  // bool
        public const long CustomSwimIdleAnimationId = 0xe0;  // int64
        public const long CustomWalkAnimationEnabled = 0x149;  // bool
        public const long CustomWalkAnimationId = 0xe8;  // int64
        public const long FallAnimationOverride = 0xf0;  // int64
        public const long IdleAltAnimationOverride = 0xf8;  // int64
        public const long IdleAnimationOverride = 0x100;  // int64
        public const long JumpAnimationOverride = 0x108;  // int64
        public const long MoodAnimationOverride = 0x110;  // int64
        public const long RunAnimationOverride = 0x118;  // int64
        public const long SwimAnimationOverride = 0x120;  // int64
        public const long SwimIdleAnimationOverride = 0x128;  // int64
        public const long WalkAnimationOverride = 0x130;  // int64
    }
    public static class AvatarBodyRules
    {
        public const long AppearanceMode = 0x150;  // Enums::AvatarSettingsAppearanceMode
        public const long AvatarType = 0x154;  // GameAvatarType
        public const long BuildMode = 0x158;  // Enums::AvatarSettingsBuildMode
        public const long CustomBodyBundleId = 0x98;  // int64
        public const long CustomBodyType = 0x15c;  // Enums::AvatarSettingsCustomBodyType
        public const long CustomBodyTypeScale = 0x120;  // NumberRange
        public const long CustomBuildBodyType = 0x120;  // NumberRange
        public const long CustomBuildHead = 0x128;  // NumberRange
        public const long CustomBuildHeight = 0x130;  // NumberRange
        public const long CustomBuildProportions = 0x138;  // NumberRange
        public const long CustomBuildWidth = 0x140;  // NumberRange
        public const long CustomEyebrowEnabled = 0x164;  // bool
        public const long CustomEyebrowId = 0xa0;  // int64
        public const long CustomEyelashEnabled = 0x165;  // bool
        public const long CustomEyelashId = 0xa8;  // int64
        public const long CustomFaceEnabled = 0x166;  // bool
        public const long CustomFaceId = 0xb0;  // int64
        public const long CustomHeadEnabled = 0x167;  // bool
        public const long CustomHeadId = 0xb8;  // int64
        public const long CustomHeadScale = 0x128;  // NumberRange
        public const long CustomHeight = 0x148;  // NumberRange
        public const long CustomHeightScale = 0x130;  // NumberRange
        public const long CustomLeftArmEnabled = 0x168;  // bool
        public const long CustomLeftArmId = 0xc0;  // int64
        public const long CustomLeftLegEnabled = 0x169;  // bool
        public const long CustomLeftLegId = 0xc8;  // int64
        public const long CustomMoodEnabled = 0x16a;  // bool
        public const long CustomMoodId = 0xd0;  // int64
        public const long CustomProportionsScale = 0x138;  // NumberRange
        public const long CustomRightArmEnabled = 0x16b;  // bool
        public const long CustomRightArmId = 0xd8;  // int64
        public const long CustomRightLegEnabled = 0x16c;  // bool
        public const long CustomRightLegId = 0xe0;  // int64
        public const long CustomTorsoEnabled = 0x16d;  // bool
        public const long CustomTorsoId = 0xe8;  // int64
        public const long CustomWidthScale = 0x140;  // NumberRange
        public const long CustomWorldHeight = 0x148;  // NumberRange
        public const long HeadOverride = 0xf0;  // int64
        public const long KeepPlayerHead = 0x16e;  // bool
        public const long LeftArmOverride = 0xf8;  // int64
        public const long LeftLegOverride = 0x100;  // int64
        public const long RightArmOverride = 0x108;  // int64
        public const long RightLegOverride = 0x110;  // int64
        public const long ScaleMode = 0x160;  // Enums::AvatarSettingsScaleMode
        public const long TorsoOverride = 0x118;  // int64
    }
    public static class AvatarClothingRules
    {
        public const long ClassicPantsOverride = 0x98;  // int64
        public const long ClassicShirtOverride = 0xa0;  // int64
        public const long ClassicTShirtOverride = 0xa8;  // int64
        public const long ClothingMode = 0x164;  // Enums::AvatarSettingsClothingMode
        public const long CustomClassicPantsAccessoryEnabled = 0x16c;  // bool
        public const long CustomClassicPantsAccessoryId = 0xb0;  // int64
        public const long CustomClassicShirtsAccessoryEnabled = 0x16d;  // bool
        public const long CustomClassicShirtsAccessoryId = 0xb8;  // int64
        public const long CustomClassicTShirtsAccessoryEnabled = 0x16e;  // bool
        public const long CustomClassicTShirtsAccessoryId = 0xc0;  // int64
        public const long CustomClothingMode = 0x168;  // Enums::AvatarSettingsCustomClothingMode
        public const long CustomDressSkirtAccessoryEnabled = 0x16f;  // bool
        public const long CustomDressSkirtAccessoryId = 0xc8;  // int64
        public const long CustomJacketAccessoryEnabled = 0x170;  // bool
        public const long CustomJacketAccessoryId = 0xd0;  // int64
        public const long CustomLeftShoesAccessoryEnabled = 0x171;  // bool
        public const long CustomLeftShoesAccessoryId = 0xd8;  // int64
        public const long CustomPantsAccessoryEnabled = 0x172;  // bool
        public const long CustomPantsAccessoryId = 0xe0;  // int64
        public const long CustomRightShoesAccessoryEnabled = 0x173;  // bool
        public const long CustomRightShoesAccessoryId = 0xe8;  // int64
        public const long CustomShirtAccessoryEnabled = 0x174;  // bool
        public const long CustomShirtAccessoryId = 0xf0;  // int64
        public const long CustomShortsAccessoryEnabled = 0x175;  // bool
        public const long CustomShortsAccessoryId = 0xf8;  // int64
        public const long CustomSweaterAccessoryEnabled = 0x176;  // bool
        public const long CustomSweaterAccessoryId = 0x100;  // int64
        public const long CustomTShirtAccessoryEnabled = 0x177;  // bool
        public const long CustomTShirtAccessoryId = 0x108;  // int64
        public const long DressSkirtAccessoryOverride = 0x110;  // int64
        public const long JacketAccessoryOverride = 0x118;  // int64
        public const long LeftShoeAccessoryOverride = 0x120;  // int64
        public const long LimitBounds = 0x158;  // Vector3
        public const long PantsAccessoryOverride = 0x128;  // int64
        public const long RightShoeAccessoryOverride = 0x130;  // int64
        public const long ShirtAccessoryOverride = 0x138;  // int64
        public const long ShortsAccessoryOverride = 0x140;  // int64
        public const long SweaterAccessoryOverride = 0x148;  // int64
        public const long TShirtAccessoryOverride = 0x150;  // int64
    }
    public static class AvatarCollisionRules
    {
        public const long BodyPartsCollidableOnDeath = 0xb0;  // bool
        public const long CollisionMode = 0xa4;  // Enums::AvatarSettingsCollisionMode
        public const long HitAndTouchDetectionMode = 0xa8;  // Enums::AvatarSettingsHitAndTouchDetectionMode
        public const long LegacyCollisionMode = 0xac;  // Enums::AvatarSettingsLegacyCollisionMode
        public const long SingleColliderSize = 0x98;  // Vector3
    }
    public static class AvatarRules
    {
        public const long AvatarType = 0x98;  // GameAvatarType
    }
    public static class AvatarSettings
    {
        public const long Loaded = 0xcc;  // bool
        public const long RulesSchemaVersion = 0xc8;  // int
    }
    public static class BaseCoreGuiConfiguration
    {
        public const long Enabled = 0x95;  // bool
    }
    public static class BaseScript
    {
        public const long Disabled = 0x10c;  // bool
        public const long LinkedSource = 0xe8;  // ContentId
        public const long RunContext = 0x108;  // Enums::RunContext
    }
    public static class BaseWrap
    {
        public const long CageMeshContent = 0xa0;  // Content
        public const long CageOrigin = 0x130;  // CoordinateFrame
        public const long HSRData = 0x120;  // SharedString
        public const long HSRMeshIdData = 0x128;  // SharedString
        public const long ImportInProcess = 0x190;  // bool
        public const long ImportOrigin = 0x160;  // CoordinateFrame
    }
    public static class Beam
    {
        public const long Brightness = 0x160;  // float
        public const long Color = 0xe0;  // ColorSequence
        public const long CurveSize0 = 0x164;  // float
        public const long CurveSize1 = 0x168;  // float
        public const long Enabled = 0x194;  // bool
        public const long FaceCamera = 0x195;  // bool
        public const long LightEmission = 0x16c;  // float
        public const long LightInfluence = 0x170;  // float
        public const long LocalTransparencyModifier = 0x174;  // float
        public const long Segments = 0x178;  // int
        public const long TextureLength = 0x17c;  // float
        public const long TextureMode = 0x180;  // TextureMode
        public const long TextureSpeed = 0x184;  // float
        public const long Transparency = 0xa0;  // NumberSequence
        public const long Width0 = 0x188;  // float
        public const long Width1 = 0x18c;  // float
        public const long ZOffset = 0x190;  // float
    }
    public static class BevelMesh
    {
        public const long Bevel = 0xc4;  // float
        public const long Bevel Roundness = 0xc8;  // float
        public const long Bulge = 0xcc;  // float
    }
    public static class BillboardGui
    {
        public const long Active = 0x71c;  // bool
        public const long AlwaysOnTop = 0x71d;  // bool
        public const long Brightness = 0x700;  // float
        public const long ClipsDescendants = 0x71e;  // bool
        public const long DistanceLowerLimit = 0x708;  // float
        public const long DistanceStep = 0x70c;  // float
        public const long DistanceUpperLimit = 0x710;  // float
        public const long ExtentsOffset = 0x6c8;  // Vector3
        public const long ExtentsOffsetWorldSpace = 0x6d4;  // Vector3
        public const long LightInfluence = 0x714;  // float
        public const long MaxDistance = 0x718;  // float
        public const long Size = 0x6b8;  // UDim2
        public const long SizeOffset = 0x6f8;  // Vector2
        public const long StudsOffset = 0x6e0;  // Vector3
        public const long StudsOffsetWorldSpace = 0x6ec;  // Vector3
    }
    public static class BinaryStringValue
    {
        public const long Value = 0xa0;  // BinaryString
    }
    public static class BloomEffect
    {
        public const long Intensity = 0x98;  // float
        public const long Size = 0x9c;  // float
        public const long Threshold = 0xa0;  // float
    }
    public static class BlurEffect
    {
        public const long Size = 0x98;  // float
    }
    public static class BodyAngularVelocity
    {
        public const long AngularVelocity = 0x278;  // Vector3
        public const long MaxTorque = 0x284;  // Vector3
        public const long P = 0x290;  // float
        public const long angularvelocity = 0x278;  // Vector3
        public const long maxTorque = 0x284;  // Vector3
    }
    public static class BodyColors
    {
        public const long HeadColor = 0xa8;  // BrickColor
        public const long HeadColor3 = 0xac;  // Color3
        public const long LeftArmColor = 0xb8;  // BrickColor
        public const long LeftArmColor3 = 0xbc;  // Color3
        public const long LeftLegColor = 0xc8;  // BrickColor
        public const long LeftLegColor3 = 0xcc;  // Color3
        public const long RightArmColor = 0xd8;  // BrickColor
        public const long RightArmColor3 = 0xdc;  // Color3
        public const long RightLegColor = 0xe8;  // BrickColor
        public const long RightLegColor3 = 0xec;  // Color3
        public const long TorsoColor = 0xf8;  // BrickColor
        public const long TorsoColor3 = 0xfc;  // Color3
    }
    public static class BodyGyro
    {
        public const long D = 0x2b4;  // float
        public const long MaxTorque = 0x2a8;  // Vector3
        public const long P = 0x2b8;  // float
        public const long maxTorque = 0x2a8;  // Vector3
    }
    public static class BodyPartDescription
    {
        public const long AssetId = 0xc0;  // int64
        public const long BodyPart = 0xd4;  // BodyPart
        public const long Color = 0xc8;  // Color3
        public const long HeadShape = 0x98;
        public const long Instance = 0xb0;
    }
    public static class BodyPosition
    {
        public const long D = 0x290;  // float
        public const long MaxForce = 0x278;  // Vector3
        public const long P = 0x294;  // float
        public const long Position = 0x284;  // Vector3
        public const long maxForce = 0x278;  // Vector3
        public const long position = 0x284;  // Vector3
    }
    public static class BodyThrust
    {
        public const long Force = 0x270;  // Vector3
        public const long Location = 0x27c;  // Vector3
        public const long force = 0x270;  // Vector3
        public const long location = 0x27c;  // Vector3
    }
    public static class BodyVelocity
    {
        public const long MaxForce = 0x278;  // Vector3
        public const long P = 0x290;  // float
        public const long Velocity = 0x284;  // Vector3
        public const long maxForce = 0x278;  // Vector3
        public const long velocity = 0x284;  // Vector3
    }
    public static class BoneInstance
    {
        public const long Transform = 0x168;  // CoordinateFrame
    }
    public static class BoolValue
    {
        public const long Value = 0xa0;  // bool
    }
    public static class BoxHandleAdornment
    {
        public const long DoubleSided = 0x19c;  // bool
        public const long Shading = 0x198;  // Enums::AdornShading
        public const long Size = 0x18c;  // Vector3
    }
    public static class BrickColorValue
    {
        public const long Value = 0xa0;  // BrickColor
    }
    public static class BubbleChatConfiguration
    {
        public const long AdorneeName = 0xa0;
        public const long BackgroundColor3 = 0xd0;  // Color3
        public const long BackgroundTransparency = 0xb8;  // double
        public const long BubbleDuration = 0xf4;  // float
        public const long BubblesSpacing = 0xf8;  // float
        public const long Enabled = 0x10c;  // bool
        public const long LocalPlayerStudsOffset = 0xdc;  // Vector3
        public const long MaxBubbles = 0xfc;  // float
        public const long MaxDistance = 0x100;  // float
        public const long MinimizeDistance = 0x104;  // float
        public const long TailVisible = 0x10d;  // bool
        public const long TextColor3 = 0xe8;  // Color3
        public const long TextSize = 0xc8;  // int64
        public const long VerticalStudsOffset = 0x108;  // float
    }
    public static class BubbleChatMessageProperties
    {
        public const long BackgroundColor3 = 0xf8;  // Color3
        public const long BackgroundTransparency = 0xe0;  // double
        public const long TailVisible = 0x110;  // bool
        public const long TextColor3 = 0x104;  // Color3
        public const long TextSize = 0xf0;  // int64
    }
    public static class CFramePose
    {
        public const long CFrame = 0xb8;  // CoordinateFrame
    }
    public static class CanvasGroup
    {
        public const long GroupColor3 = 0x99c;  // Color3; heuristic decode, passed live check
        public const long GroupTransparency = 0x9a8;  // float; heuristic decode, passed live check
        public const long ResolutionScale = 0x9ac;  // float
    }
    public static class CapturesViewConfiguration
    {
        public const long Open = 0x96;  // bool
    }
    public static class ChannelTabsConfiguration
    {
        public const long BackgroundColor3 = 0xc0;  // Color3
        public const long BackgroundTransparency = 0xa0;  // double
        public const long Enabled = 0x10c;  // bool
        public const long HoverBackgroundColor3 = 0xcc;  // Color3
        public const long SelectedTabTextColor3 = 0xd8;  // Color3
        public const long TextColor3 = 0xe4;  // Color3
        public const long TextSize = 0xb0;  // int64
        public const long TextStrokeColor3 = 0xf0;  // Color3
        public const long TextStrokeTransparency = 0xb8;  // double
    }
    public static class CharacterMesh
    {
        public const long BodyPart = 0x118;  // BodyPart
    }
    public static class ChatInputBarConfiguration
    {
        public const long AutocompleteEnabled = 0x124;  // bool
        public const long BackgroundColor3 = 0xe0;  // Color3
        public const long BackgroundTransparency = 0xc0;  // double
        public const long Enabled = 0x125;  // bool
        public const long IsFocusedWrite = 0x126;  // bool
        public const long KeyboardKeyCode = 0x120;  // KeyCode
        public const long PlaceholderColor3 = 0xec;  // Color3
        public const long TargetTextChannel = 0xa0;
        public const long TextBox = 0xb0;
        public const long TextColor3 = 0xf8;  // Color3
        public const long TextSize = 0xd0;  // int64
        public const long TextStrokeColor3 = 0x104;  // Color3
        public const long TextStrokeTransparency = 0xd8;  // double
    }
    public static class ChatService
    {
        public const long BubbleChatEnabled = 0x108;  // bool
        public const long IsAutoMigrated = 0x109;  // bool
        public const long LoadDefaultChat = 0x10a;  // bool
        public const long ModerationMode = 0xa8;
    }
    public static class ChatWindowConfiguration
    {
        public const long AbsolutePositionWrite = 0xe4;  // Vector2
        public const long AbsoluteSizeWrite = 0xec;  // Vector2
        public const long BackgroundColor3 = 0xc0;  // Color3
        public const long BackgroundTransparency = 0xa0;  // double
        public const long Enabled = 0x108;  // bool
        public const long HeightScale = 0xf4;  // float
        public const long HorizontalAlignment = 0xf8;  // Enums::HorizontalAlignmentEnum::HorizontalAlignment
        public const long TextChannelDisplayMode = 0xfc;  // TextChannelDisplayMode
        public const long TextColor3 = 0xcc;  // Color3
        public const long TextSize = 0xb0;  // int64
        public const long TextStrokeColor3 = 0xd8;  // Color3
        public const long TextStrokeTransparency = 0xb8;  // double
        public const long VerticalAlignment = 0x100;  // Enums::VerticalAlignmentEnum::VerticalAlignment
        public const long WidthScale = 0x104;  // float
    }
    public static class ChatWindowMessageProperties
    {
        public const long PrefixTextProperties = 0xe0;
        public const long TextColor3 = 0x100;  // Color3
        public const long TextSize = 0x118;  // int
        public const long TextStrokeColor3 = 0x10c;  // Color3
        public const long TextStrokeTransparency = 0xf8;  // double
    }
    public static class ClickDetector
    {
        public const long MaxActivationDistance = 0xc8;  // float
    }
    public static class ClimbController
    {
        public const long AccelerationTime = 0xc0;  // float
        public const long BalanceMaxTorque = 0xc4;  // float
        public const long BalanceSpeed = 0xc8;  // float
        public const long MoveMaxForce = 0xcc;  // float
    }
    public static class Clothing
    {
        public const long Color3 = 0xf8;  // Color3
    }
    public static class CloudClientService
    {
        public const long RobloxRealityFilterEnabled = 0xba;  // bool
    }
    public static class Clouds
    {
        public const long Cover = 0xa4;  // float
        public const long Density = 0xa8;  // float
        public const long Enabled = 0xac;  // bool
    }
    public static class Color3Value
    {
        public const long Value = 0xa0;  // Color3
    }
    public static class ColorCorrectionEffect
    {
        public const long Brightness = 0xa4;  // float
        public const long Contrast = 0xa8;  // float
        public const long Saturation = 0xac;  // float
        public const long TintColor = 0x98;  // Color3
    }
    public static class ColorGradingEffect
    {
        public const long TonemapperPreset = 0x98;  // TonemapperPreset
    }
    public static class CompositeValueCurve
    {
        public const long CurveType = 0x98;  // CompositeValueCurveType
    }
    public static class ConeHandleAdornment
    {
        public const long DoubleSided = 0x198;  // bool
        public const long Height = 0x18c;  // float
        public const long Hollow = 0x199;  // bool
        public const long Radius = 0x190;  // float
        public const long Shading = 0x194;  // Enums::AdornShading
    }
    public static class Constraints_AlignOrientation
    {
        public const long AlignType = 0x188;
        public const long LookAtPosition = 0x17c;  // Vector3
        public const long MaxAngularVelocity = 0x18c;  // float
        public const long MaxTorque = 0x190;  // float
        public const long Mode = 0x194;
        public const long PrimaryAxis = 0x158;  // Vector3
        public const long PrimaryAxisOnly = 0x19c;  // bool
        public const long ReactionTorqueEnabled = 0x19d;  // bool
        public const long Responsiveness = 0x198;  // float
        public const long RigidityEnabled = 0x19e;  // bool
        public const long SecondaryAxis = 0x15c;  // Vector3
    }
    public static class Constraints_AlignPosition
    {
        public const long ApplyAtCenterOfMass = 0x188;  // bool
        public const long ForceLimitMode = 0x170;
        public const long ForceRelativeTo = 0x174;
        public const long MaxAxesForce = 0x158;  // Vector3
        public const long MaxForce = 0x178;  // float
        public const long MaxVelocity = 0x17c;  // float
        public const long Mode = 0x180;
        public const long Position = 0x164;  // Vector3
        public const long ReactionForceEnabled = 0x189;  // bool
        public const long Responsiveness = 0x184;  // float
        public const long RigidityEnabled = 0x18a;  // bool
    }
    public static class Constraints_AngularVelocityActuator
    {
        public const long AngularVelocity = 0x158;  // Vector3
        public const long MaxTorque = 0x164;  // float
        public const long ReactionTorqueEnabled = 0x16c;  // bool
        public const long RelativeTo = 0x168;
    }
    public static class Constraints_AnimationConstraint
    {
        public const long AngularDamping = 0x158;  // float
        public const long AngularStrength = 0x15c;  // float
        public const long EnableSkinning = 0x170;  // bool
        public const long IsKinematic = 0x171;  // bool
        public const long LinearDamping = 0x160;  // float
        public const long LinearStrength = 0x164;  // float
        public const long MaxForce = 0x168;  // float
        public const long MaxTorque = 0x16c;  // float
    }
    public static class Constraints_BallSocketConstraint
    {
        public const long EnableSkinning = 0x170;  // bool
        public const long LimitsEnabled = 0x171;  // bool
        public const long Radius = 0x15c;  // float
        public const long Restitution = 0x160;  // float
        public const long TwistLimitsEnabled = 0x172;  // bool
        public const long TwistLowerAngle = 0x164;  // float
        public const long TwistUpperAngle = 0x168;  // float
        public const long UpperAngle = 0x16c;  // float
    }
    public static class Constraints_Constraint
    {
        public const long Color = 0xd8;  // BrickColor
        public const long Enabled = 0xa1;  // bool
        public const long Visible = 0xdc;  // bool
    }
    public static class Constraints_CylindricalConstraint
    {
        public const long AngularActuatorType = 0x1b8;
        public const long AngularLimitsEnabled = 0x1e8;  // bool
        public const long AngularResponsiveness = 0x1bc;  // float
        public const long AngularRestitution = 0x1c0;  // float
        public const long AngularSpeed = 0x1c4;  // float
        public const long AngularVelocity = 0x1c8;  // float
        public const long InclinationAngle = 0x1cc;  // float
        public const long LowerAngle = 0x1d0;  // float
        public const long MotorMaxAngularAcceleration = 0x1d4;  // float
        public const long MotorMaxTorque = 0x1d8;  // float
        public const long RotationAxisVisible = 0x1e9;  // bool
        public const long ServoMaxTorque = 0x1dc;  // float
        public const long SoftlockAngularServoUponReachingTarget = 0x1ea;  // bool
        public const long TargetAngle = 0x1e0;  // float
        public const long UpperAngle = 0x1e4;  // float
    }
    public static class Constraints_HingeConstraint
    {
        public const long ActuatorType = 0x158;
        public const long AngularResponsiveness = 0x15c;  // float
        public const long AngularSpeed = 0x160;  // float
        public const long AngularVelocity = 0x164;  // float
        public const long LimitsEnabled = 0x188;  // bool
        public const long LowerAngle = 0x168;  // float
        public const long MotorMaxAcceleration = 0x16c;  // float
        public const long MotorMaxTorque = 0x170;  // float
        public const long Radius = 0x174;  // float
        public const long Restitution = 0x178;  // float
        public const long ServoMaxTorque = 0x17c;  // float
        public const long SoftlockServoUponReachingTarget = 0x189;  // bool
        public const long TargetAngle = 0x180;  // float
        public const long UpperAngle = 0x184;  // float
    }
    public static class Constraints_LineForce
    {
        public const long ApplyAtCenterOfMass = 0x160;  // bool
        public const long InverseSquareLaw = 0x161;  // bool
        public const long Magnitude = 0x158;  // float
        public const long MaxForce = 0x15c;  // float
        public const long ReactionForceEnabled = 0x162;  // bool
    }
    public static class Constraints_LinearVelocity
    {
        public const long ForceLimitMode = 0x14;  // at *(object + 0x160) + this
        public const long ForceLimitsEnabled = 0x9;  // bool; at *(object + 0x160) + this
        public const long LineDirection = 0x180;  // Vector3
        public const long MaxAxesForce = 0x220;  // Vector3
        public const long MaxForce = 0x10;  // float; at *(object + 0x160) + this
        public const long MaxPlanarAxesForce = 0x1b0;  // Vector2
        public const long PlaneVelocity = 0x118;  // Vector2; at *(object + 0x200) + this
        public const long PrimaryTangentAxis = 0x1e8;  // Vector3
        public const long ReactionForceEnabled = 0x15c;  // bool
        public const long RelativeTo = 0xc;  // at *(object + 0x160) + this
        public const long SecondaryTangentAxis = 0x1f4;  // Vector3
        public const long VectorVelocity = 0x22c;  // Vector3
        public const long VelocityConstraintMode = 0x158;
    }
    public static class Constraints_NoCollisionConstraint
    {
        public const long Enabled = 0xc0;  // bool
    }
    public static class Constraints_RigidConstraint
    {
        public const long EnableSkinning = 0x150;  // bool
    }
    public static class Constraints_RodConstraint
    {
        public const long Length = 0x158;  // float
        public const long LimitAngle0 = 0x15c;  // float
        public const long LimitAngle1 = 0x160;  // float
        public const long LimitsEnabled = 0x168;  // bool
        public const long Thickness = 0x164;  // float
    }
    public static class Constraints_RopeConstraint
    {
        public const long Length = 0x158;  // float
        public const long Restitution = 0x15c;  // float
        public const long Thickness = 0x160;  // float
        public const long WinchEnabled = 0x174;  // bool
        public const long WinchForce = 0x164;  // float
        public const long WinchResponsiveness = 0x168;  // float
        public const long WinchSpeed = 0x16c;  // float
        public const long WinchTarget = 0x170;  // float
    }
    public static class Constraints_SlidingBallConstraint
    {
        public const long ActuatorType = 0x158;
        public const long LimitsEnabled = 0x188;  // bool
        public const long LinearResponsiveness = 0x15c;  // float
        public const long LowerLimit = 0x160;  // float
        public const long MotorMaxAcceleration = 0x164;  // float
        public const long MotorMaxForce = 0x168;  // float
        public const long Restitution = 0x16c;  // float
        public const long ServoMaxForce = 0x170;  // float
        public const long Size = 0x174;  // float
        public const long SoftlockServoUponReachingTarget = 0x189;  // bool
        public const long Speed = 0x178;  // float
        public const long TargetPosition = 0x17c;  // float
        public const long UpperLimit = 0x180;  // float
        public const long Velocity = 0x184;  // float
    }
    public static class Constraints_SpringConstraint
    {
        public const long Coils = 0x158;  // float
        public const long Damping = 0x15c;  // float
        public const long FreeLength = 0x160;  // float
        public const long LimitsEnabled = 0x17c;  // bool
        public const long MaxForce = 0x164;  // float
        public const long MaxLength = 0x168;  // float
        public const long MinLength = 0x16c;  // float
        public const long Radius = 0x170;  // float
        public const long Stiffness = 0x174;  // float
        public const long Thickness = 0x178;  // float
    }
    public static class Constraints_Torque
    {
        public const long RelativeTo = 0x164;
    }
    public static class Constraints_TorsionSpringConstraint
    {
        public const long Coils = 0x158;  // float
        public const long Damping = 0x15c;  // float
        public const long LimitEnabled = 0x174;  // bool
        public const long LimitsEnabled = 0x174;  // bool
        public const long MaxAngle = 0x160;  // float
        public const long MaxTorque = 0x164;  // float
        public const long Radius = 0x168;  // float
        public const long Restitution = 0x16c;  // float
        public const long Stiffness = 0x170;  // float
    }
    public static class Constraints_UniversalConstraint
    {
        public const long LimitsEnabled = 0x164;  // bool
        public const long MaxAngle = 0x158;  // float
        public const long Radius = 0x15c;  // float
        public const long Restitution = 0x160;  // float
    }
    public static class Constraints_VectorForce
    {
        public const long ApplyAtCenterOfMass = 0x168;  // bool
        public const long Force = 0x158;  // Vector3
        public const long RelativeTo = 0x164;
    }
    public static class Constraints_WeldConstraint
    {
        public const long Enabled = 0xc0;  // bool
    }
    public static class ControlState
    {
        public const long StateSchema = 0x98;  // BinaryString
    }
    public static class ControllerBase
    {
        public const long BalanceRigidityEnabled = 0xa5;  // bool
        public const long MoveSpeedFactor = 0xa0;  // float
    }
    public static class ControllerManager
    {
        public const long ActiveController = 0xa0;
        public const long BaseMoveSpeed = 0x104;  // float
        public const long BaseTurnSpeed = 0x108;  // float
        public const long ClimbSensor = 0xb0;
        public const long FacingDirection = 0xe0;  // Vector3
        public const long GroundSensor = 0xc0;
        public const long MovingDirection = 0xec;  // Vector3
        public const long RootPart = 0xd0;
        public const long UpDirection = 0xf8;  // Vector3
    }
    public static class ControllerPartSensor
    {
        public const long LadderSearchHeight = 0x27c;  // float
        public const long LadderSearchOffset = 0x280;  // float
        public const long SearchDistance = 0x284;  // float
        public const long SensorMode = 0x28c;  // SensorMode
    }
    public static class CoreGuiConfiguration
    {
        public const long CapturesViewConfiguration = 0xa8;
        public const long PlayerListConfiguration = 0xb8;
        public const long SelfViewConfiguration = 0xc8;
    }
    public static class CustomEvent
    {
        public const long PersistedCurrentValue = 0x98;  // float
    }
    public static class CustomParticleEmitter
    {
        public const long Acceleration = 0x1c0;  // Vector3
        public const long Brightness = 0x1fc;  // float
        public const long Color = 0x160;  // ColorSequence
        public const long Drag = 0x200;  // float
        public const long EmissionDirection = 0x204;  // NormalId
        public const long Enabled = 0x248;  // bool
        public const long FlipbookBlendFrames = 0x249;  // bool
        public const long FlipbookFramerate = 0x1cc;  // NumberRange
        public const long FlipbookLayout = 0x208;  // ParticleFlipbookLayout
        public const long FlipbookMode = 0x20c;  // ParticleFlipbookMode
        public const long FlipbookSizeX = 0x210;  // int
        public const long FlipbookSizeY = 0x214;  // int
        public const long FlipbookStartRandom = 0x24a;  // bool
        public const long Lifetime = 0x1d4;  // NumberRange
        public const long LightEmission = 0x218;  // float
        public const long LightInfluence = 0x21c;  // float
        public const long LocalTransparencyModifier = 0x220;  // float
        public const long LockedToPart = 0x24b;  // bool
        public const long Orientation = 0x224;  // ParticleOrientation
        public const long Rate = 0x228;  // float
        public const long RotSpeed = 0x1dc;  // NumberRange
        public const long Rotation = 0x1e4;  // NumberRange
        public const long Shape = 0x22c;  // ParticleEmitterShape
        public const long ShapeInOut = 0x230;  // ParticleEmitterShapeInOut
        public const long ShapePartial = 0x234;  // float
        public const long ShapeStyle = 0x238;  // ParticleEmitterShapeStyle
        public const long Size = 0xa0;  // NumberSequence
        public const long Speed = 0x1ec;  // NumberRange
        public const long SpreadAngle = 0x1f4;  // Vector2
        public const long Squash = 0xe0;  // NumberSequence
        public const long TimeScale = 0x23c;  // float
        public const long Transparency = 0x120;  // NumberSequence
        public const long VelocityInheritance = 0x240;  // float
        public const long VelocitySpread = 0x1f4;  // float
        public const long WindAffectsDrag = 0x24c;  // bool
        public const long ZOffset = 0x244;  // float
    }
    public static class CylinderHandleAdornment
    {
        public const long Angle = 0x18c;  // float
        public const long DoubleSided = 0x1a0;  // bool
        public const long Height = 0x190;  // float
        public const long InnerRadius = 0x194;  // float
        public const long Radius = 0x198;  // float
        public const long Shading = 0x19c;  // Enums::AdornShading
    }
    public static class DataModelMesh
    {
        public const long Offset = 0xa0;  // Vector3
        public const long Scale = 0xac;  // Vector3
        public const long VertexColor = 0xb8;  // Vector3
    }
    public static class DataStoreGetOptions
    {
        public const long UseCache = 0x95;  // bool
    }
    public static class DataStoreOptions
    {
        public const long AllScopes = 0x95;  // bool
    }
    public static class DataStoreService
    {
        public const long AutomaticRetry = 0xb0;  // bool
        public const long LegacyNamingScheme = 0xb1;  // bool
    }
    public static class DebrisService
    {
        public const long MaxItems = 0xb0;  // int
    }
    public static class Decal
    {
        public const long AutoLocalize = 0x240;  // bool
        public const long Color3 = 0x1f8;  // Color3
        public const long EmissiveMaskContent = 0xc8;  // Content
        public const long EmissiveStrength = 0x220;  // float
        public const long EmissiveTint = 0x204;  // Color3
        public const long LocalTransparencyModifier = 0x224;  // float
        public const long MetalnessMapContent = 0x118;  // Content
        public const long NormalMapContent = 0x140;  // Content
        public const long ResampleMode = 0x228;  // Enums::ImageResampleMode
        public const long Rotation = 0x22c;  // float
        public const long RoughnessMapContent = 0x168;  // Content
        public const long Shiny = 0x230;  // float
        public const long Specular = 0x234;  // float
        public const long TextureContent = 0x190;  // Content
        public const long TexturePackContent = 0x1b8;  // Content
        public const long TexturePackMetadata = 0x1e0;
        public const long Transparency = 0x238;  // float
        public const long UVOffset = 0x210;  // Vector2
        public const long UVScale = 0x218;  // Vector2
        public const long ZIndex = 0x23c;  // int
    }
    public static class DeferredAssetManagerService
    {
        public const long JoiningPlaceId = 0xb0;  // int64
        public const long JoiningUniverseId = 0xb8;  // int64
        public const long PregameLoadingScreenOnly = 0xc0;  // bool
    }
    public static class DepthOfFieldEffect
    {
        public const long FarIntensity = 0x98;  // float
        public const long FocusDistance = 0x9c;  // float
        public const long InFocusRadius = 0xa0;  // float
        public const long NearIntensity = 0xa4;  // float
    }
    public static class DialogChoice
    {
        public const long GoodbyeChoiceActive = 0xe8;  // bool
        public const long GoodbyeDialog = 0xa0;
        public const long ResponseDialog = 0xb8;
        public const long UserDialog = 0xd0;
    }
    public static class DialogRoot
    {
        public const long BehaviorType = 0xd4;  // Enums::DialogBehaviorTypeEnum::DialogBehaviorType
        public const long ConversationDistance = 0xd8;  // float
        public const long GoodbyeChoiceActive = 0xe8;  // bool
        public const long GoodbyeDialog = 0x98;
        public const long InUse = 0xe9;  // bool
        public const long InitialPrompt = 0xb0;
        public const long Purpose = 0xdc;  // Enums::DialogPurposeEnum::DialogPurpose
        public const long Tone = 0xe0;  // Enums::DialogToneEnum::DialogTone
        public const long TriggerDistance = 0xe4;  // float
        public const long TriggerOffset = 0xc8;  // Vector3
    }
    public static class DigitsRigDescription
    {
        public const long Index1 = 0x98;
        public const long Index1TposeAdjustment = 0x188;  // CoordinateFrame
        public const long Index2 = 0xa8;
        public const long Index2TposeAdjustment = 0x1b8;  // CoordinateFrame
        public const long Index3 = 0xb8;
        public const long Index3TposeAdjustment = 0x1e8;  // CoordinateFrame
        public const long IndexRange = 0x458;  // Vector3
        public const long IndexSize = 0x494;  // float
        public const long Middle1 = 0xc8;
        public const long Middle1TposeAdjustment = 0x218;  // CoordinateFrame
        public const long Middle2 = 0xd8;
        public const long Middle2TposeAdjustment = 0x248;  // CoordinateFrame
        public const long Middle3 = 0xe8;
        public const long Middle3TposeAdjustment = 0x278;  // CoordinateFrame
        public const long MiddleRange = 0x464;  // Vector3
        public const long MiddleSize = 0x498;  // float
        public const long Pinky1 = 0xf8;
        public const long Pinky1TposeAdjustment = 0x2a8;  // CoordinateFrame
        public const long Pinky2 = 0x108;
        public const long Pinky2TposeAdjustment = 0x2d8;  // CoordinateFrame
        public const long Pinky3 = 0x118;
        public const long Pinky3TposeAdjustment = 0x308;  // CoordinateFrame
        public const long PinkyRange = 0x470;  // Vector3
        public const long PinkySize = 0x49c;  // float
        public const long Ring1 = 0x128;
        public const long Ring1TposeAdjustment = 0x338;  // CoordinateFrame
        public const long Ring2 = 0x138;
        public const long Ring2TposeAdjustment = 0x368;  // CoordinateFrame
        public const long Ring3 = 0x148;
        public const long Ring3TposeAdjustment = 0x398;  // CoordinateFrame
        public const long RingRange = 0x47c;  // Vector3
        public const long RingSize = 0x4a0;  // float
        public const long Side = 0x4a4;  // Enums::DigitsSide
        public const long Thumb1 = 0x158;
        public const long Thumb1TposeAdjustment = 0x3c8;  // CoordinateFrame
        public const long Thumb2 = 0x168;
        public const long Thumb2TposeAdjustment = 0x3f8;  // CoordinateFrame
        public const long Thumb3 = 0x178;
        public const long Thumb3TposeAdjustment = 0x428;  // CoordinateFrame
        public const long ThumbRange = 0x488;  // Vector3
        public const long ThumbSize = 0x4a8;  // float
    }
    public static class DoubleConstrainedValue
    {
        public const long MaxValue = 0xa0;  // double
        public const long MinValue = 0xa8;  // double
    }
    public static class DoublePose
    {
        public const long Value = 0xb8;  // double
    }
    public static class DoubleValue
    {
        public const long Value = 0xa0;  // double
    }
    public static class DragDetector
    {
        public const long ApplyAtCenterOfMass = 0x288;  // bool
        public const long Axis = 0x218;  // Vector3
        public const long DragFrame = 0x1b8;  // CoordinateFrame
        public const long DragStyle = 0x254;  // DragDetectorDragStyle
        public const long Enabled = 0x289;  // bool
        public const long GamepadModeSwitchKeyCode = 0x258;  // KeyCode
        public const long KeyboardModeSwitchKeyCode = 0x25c;  // KeyCode
        public const long MaxDragAngle = 0x260;  // float
        public const long MaxDragTranslation = 0x224;  // Vector3
        public const long MaxForce = 0x264;  // float
        public const long MaxTorque = 0x268;  // float
        public const long MinDragAngle = 0x26c;  // float
        public const long MinDragTranslation = 0x230;  // Vector3
        public const long PermissionPolicy = 0x270;  // DragDetectorPermissionPolicy
        public const long PhysicalDragHitPoint = 0x23c;  // Vector3
        public const long PhysicalDragIsInVR = 0x28a;  // bool
        public const long PhysicalDragTargetFrame = 0x1e8;  // CoordinateFrame
        public const long ResponseStyle = 0x274;  // DragDetectorResponseStyle
        public const long Responsiveness = 0x278;  // float
        public const long RunLocally = 0x28b;  // bool
        public const long SecondaryAxis = 0x248;  // Vector3
        public const long TrackballRadialPullFactor = 0x27c;  // float
        public const long TrackballRollFactor = 0x280;  // float
        public const long VRSwitchKeyCode = 0x284;  // KeyCode
    }
    public static class EditableImage
    {
        public const long IsReplicatedCopy = 0xc0;  // bool
    }
    public static class EditableMesh
    {
        public const long IsReplicatedCopy = 0xc1;  // bool
    }
    public static class EditableService
    {
        public const long EditableStatus = 0xb0;  // Enums::EditableStatusEnum::EditableStatus
    }
    public static class EulerRotationCurve
    {
        public const long RotationOrder = 0x98;  // EulerAngles::RotationOrder
    }
    public static class ExperienceInviteOptions
    {
        public const long InviteMessageId = 0x98;
        public const long InviteUser = 0xe0;  // int64
        public const long LaunchData = 0xb0;
        public const long PromptMessage = 0xc8;
    }
    public static class ExperienceStateCapture_ExperienceStateRecordingService
    {
        public const long IsServerDataModelRecorderActive = 0xb0;  // bool
    }
    public static class ExperienceStateCaptureService
    {
        public const long HiddenSelectionEnabled = 0xa8;  // bool
        public const long SelectionMode = 0xa4;  // Enums::ExperienceStateCaptureSelectionMode
    }
    public static class Explosion
    {
        public const long BlastPressure = 0xa4;  // float
        public const long BlastRadius = 0xa8;  // float
        public const long DestroyJointRadiusPercent = 0xac;  // float
        public const long ExplosionType = 0xb0;  // Enums::ExplosionTypeEnum::ExplosionType
        public const long LocalTransparencyModifier = 0xb4;  // float
        public const long TimeScale = 0xb8;  // float
        public const long Visible = 0xbc;  // bool
    }
    public static class FaceControls
    {
        public const long Corrugator = 0xc8;  // float
        public const long EyesLookDown = 0xcc;  // float
        public const long EyesLookLeft = 0xd0;  // float
        public const long EyesLookRight = 0xd4;  // float
        public const long EyesLookUp = 0xd8;  // float
        public const long FlatPucker = 0xdc;  // float
        public const long Funneler = 0xe0;  // float
        public const long InternalOverrideFACSData = 0xa0;  // BinaryString
        public const long JawDrop = 0xe4;  // float
        public const long JawLeft = 0xe8;  // float
        public const long JawRight = 0xec;  // float
        public const long LeftBrowLowerer = 0xf0;  // float
        public const long LeftCheekPuff = 0xf4;  // float
        public const long LeftCheekRaiser = 0xf8;  // float
        public const long LeftDimpler = 0xfc;  // float
        public const long LeftEyeClosed = 0x100;  // float
        public const long LeftEyeUpperLidRaiser = 0x104;  // float
        public const long LeftInnerBrowRaiser = 0x108;  // float
        public const long LeftLipCornerDown = 0x10c;  // float
        public const long LeftLipCornerPuller = 0x110;  // float
        public const long LeftLipStretcher = 0x114;  // float
        public const long LeftLowerLipDepressor = 0x118;  // float
        public const long LeftNoseWrinkler = 0x11c;  // float
        public const long LeftOuterBrowRaiser = 0x120;  // float
        public const long LeftUpperLipRaiser = 0x124;  // float
        public const long LipPresser = 0x128;  // float
        public const long LipsTogether = 0x12c;  // float
        public const long LowerLipSuck = 0x130;  // float
        public const long MouthLeft = 0x134;  // float
        public const long MouthRight = 0x138;  // float
        public const long Pucker = 0x13c;  // float
        public const long RightBrowLowerer = 0x140;  // float
        public const long RightCheekPuff = 0x144;  // float
        public const long RightCheekRaiser = 0x148;  // float
        public const long RightDimpler = 0x14c;  // float
        public const long RightEyeClosed = 0x150;  // float
        public const long RightEyeUpperLidRaiser = 0x154;  // float
        public const long RightInnerBrowRaiser = 0x158;  // float
        public const long RightLipCornerDown = 0x15c;  // float
        public const long RightLipCornerPuller = 0x160;  // float
        public const long RightLipStretcher = 0x164;  // float
        public const long RightLowerLipDepressor = 0x168;  // float
        public const long RightNoseWrinkler = 0x16c;  // float
        public const long RightOuterBrowRaiser = 0x170;  // float
        public const long RightUpperLipRaiser = 0x174;  // float
        public const long TongueDown = 0x178;  // float
        public const long TongueOut = 0x17c;  // float
        public const long TongueUp = 0x180;  // float
        public const long UpperLipSuck = 0x184;  // float
    }
    public static class FaceInstance
    {
        public const long Face = 0x98;  // NormalId
    }
    public static class FacialAnimationStreamingServiceV2
    {
        public const long ServiceState = 0xf0;  // int
    }
    public static class Feature
    {
        public const long FaceId = 0x98;  // NormalId
        public const long InOut = 0x9c;  // Enums::InOutEnum::InOut
        public const long LeftRight = 0xa0;  // Enums::LeftRightEnum::LeftRight
        public const long TopBottom = 0xa4;  // Enums::TopBottomEnum::TopBottom
    }
    public static class FeatureMatchingTable
    {
        public const long Data = 0xb8;  // SharedString
    }
    public static class FileSyncItem
    {
        public const long AutoSync = 0xc0;  // bool
        public const long Enabled = 0xc1;  // bool
        public const long Target = 0xb0;
    }
    public static class Fire
    {
        public const long Color = 0xa0;  // Color3
        public const long Enabled = 0xc8;  // bool
        public const long Heat = 0xc0;  // float
        public const long LocalTransparencyModifier = 0xb8;  // float
        public const long SecondaryColor = 0xac;  // Color3
        public const long Size = 0xc4;  // float
        public const long TimeScale = 0xbc;  // float
        public const long heat_xml = 0xc0;  // float
        public const long size = 0xc4;  // float
        public const long size_xml = 0xc4;  // float
    }
    public static class Flag
    {
        public const long TeamColor = 0x530;  // BrickColor
    }
    public static class FlagStand
    {
        public const long TeamColor = 0x1b8;  // BrickColor
    }
    public static class FloorWire
    {
        public const long CycleOffset = 0x128;  // float
        public const long StudsBetweenTextures = 0x12c;  // float
        public const long TextureSize = 0x120;  // Vector2
        public const long Velocity = 0x130;  // float
        public const long WireRadius = 0x134;  // float
    }
    public static class ForceField
    {
        public const long Visible = 0xa0;  // bool
    }
    public static class FormFactorPart
    {
        public const long FormFactor = 0x1a8;  // Enums::FormFactorEnum::FormFactor
        public const long formFactor = 0x1a8;  // Enums::FormFactorEnum::FormFactor
        public const long formFactorRaw = 0x1a8;  // Enums::FormFactorEnum::FormFactor
    }
    public static class FunctionalTest
    {
        public const long AllowSleep = 0xb8;  // bool
        public const long Description = 0x98;
        public const long HasMigratedSettingsToTestService = 0xb9;  // bool
        public const long Is30FpsThrottleEnabled = 0xba;  // bool
        public const long PhysicsEnvironmentalThrottle = 0xbb;  // bool
        public const long Timeout = 0xb0;  // double
    }
    public static class GamepadService
    {
        public const long GamepadCursorEnabled = 0xb0;  // bool
    }
    public static class Glue
    {
        public const long F0 = 0x170;  // Vector3
        public const long F1 = 0x17c;  // Vector3
        public const long F2 = 0x188;  // Vector3
        public const long F3 = 0x194;  // Vector3
    }
    public static class GroundController
    {
        public const long AccelerationLean = 0xc0;  // float
        public const long AccelerationTime = 0xc4;  // float
        public const long BalanceMaxTorque = 0xc8;  // float
        public const long BalanceSpeed = 0xcc;  // float
        public const long DecelerationTime = 0xd0;  // float
        public const long Friction = 0xd4;  // float
        public const long FrictionWeight = 0xd8;  // float
        public const long GroundOffset = 0xdc;  // float
        public const long StandForce = 0xe0;  // float
        public const long StandSpeed = 0xe4;  // float
        public const long TurnSpeedFactor = 0xe8;  // float
    }
    public static class GuiBase2d
    {
        public const long SelectionBehaviorDown = 0x108;  // Enums::SelectionBehavior
        public const long SelectionBehaviorLeft = 0x10c;  // Enums::SelectionBehavior
        public const long SelectionBehaviorRight = 0x110;  // Enums::SelectionBehavior
        public const long SelectionBehaviorUp = 0x114;  // Enums::SelectionBehavior
    }
    public static class GuiBase3d
    {
        public const long Color = 0xc0;  // BrickColor
        public const long Color3 = 0xc0;  // Color3
        public const long Transparency = 0xcc;  // float
        public const long Visible = 0xd0;  // bool
    }
    public static class GuiButton
    {
        public const long AutoButtonColor = 0x9ec;  // bool
        public const long MouseButton1ClickConnectionCount = 0x9d0;  // int
        public const long MouseButton1DownConnectionCount = 0x9d4;  // int
        public const long MouseButton1UpConnectionCount = 0x9d8;  // int
        public const long MouseButton2ClickConnectionCount = 0x9dc;  // int
        public const long MouseButton2DownConnectionCount = 0x9e0;  // int
        public const long MouseButton2UpConnectionCount = 0x9e4;  // int
        public const long Selected = 0x9ee;  // bool
    }
    public static class GuiImageButton
    {
        public const long ImageColor3 = 0xd98;  // Color3; heuristic decode, passed live check
    }
    public static class GuiLayerCollector
    {
        public const long Enabled = 0x494;  // bool
        public const long ResetOnSpawn = 0x495;  // bool
        public const long TabKeyboardNavigation = 0x496;  // bool
        public const long ZIndexBehavior = 0x490;  // Enums::ZIndexBehaviorEnum::ZIndexBehavior
    }
    public static class GuiObject
    {
        public const long BackgroundColor3 = 0x510;  // Color3; heuristic decode, passed live check
        public const long BorderColor3 = 0x51c;  // Color3; heuristic decode, passed live check
        public const long DragBeginConnectionCount = 0x540;  // int
        public const long DragStoppedConnectionCount = 0x544;  // int
        public const long Draggable = 0x57a;  // bool
        public const long InputSink = 0x56c;  // Enums::InputSink
        public const long Interactable = 0x57b;  // bool
        public const long MouseEnterConnectionCount = 0x550;  // int
        public const long MouseLeaveConnectionCount = 0x554;  // int
        public const long MouseMovedConnectionCount = 0x558;  // int
        public const long MouseWheelBackwardConnectionCount = 0x55c;  // int
        public const long MouseWheelForwardConnectionCount = 0x560;  // int
        public const long Position = 0x4e0;  // UDim2
        public const long Rotation = 0x564;  // float
        public const long SelectionImageObject = 0x4d0;
        public const long Sink = 0x56c;  // Enums::InputSink
        public const long Size = 0x500;  // UDim2
    }
    public static class GuiService
    {
        public const long DisplayScalingMode = 0x128;  // Enums::DisplayScalingMode
        public const long GuiNavigationEnabled = 0x134;  // bool
        public const long TouchControlsEnabled = 0x136;  // bool
    }
    public static class GuiTextButton
    {
        public const long Confidential = 0xcc;  // bool
        public const long LocalizationMatchIdentifier = 0x20;
        public const long LocalizationMatchedSourceText = 0x38;
    }
    public static class HandleAdornment
    {
        public const long AdornCullingMode = 0x13c;  // AdornCullingMode
        public const long AlwaysOnTop = 0x144;  // bool
        public const long SizeRelativeOffset = 0x130;  // Vector3
    }
    public static class Handles
    {
        public const long Faces = 0x104;  // Faces
        public const long MouseButton1DownConnectionCount = 0x108;  // int
        public const long MouseButton1UpConnectionCount = 0x10c;  // int
        public const long MouseDragConnectionCount = 0x110;  // int
        public const long MouseEnterConnectionCount = 0x114;  // int
        public const long MouseLeaveConnectionCount = 0x118;  // int
        public const long Style = 0x11c;  // Enums::HandlesStyleEnum::VisualStyle
    }
    public static class HapticEffect
    {
        public const long Looped = 0xcc;  // bool
        public const long Position = 0xb8;  // Vector3
        public const long Radius = 0xc4;  // float
        public const long Type = 0xc8;  // Enums::HapticEffectType
        public const long WaveformData = 0xa0;  // BinaryString
    }
    public static class HiddenSurfaceRemovalAsset
    {
        public const long HSRMeshIdData = 0xb0;  // BinaryString
    }
    public static class Highlight
    {
        public const long DepthMode = 0xc8;  // Enums::HighlightDepthModeEnum::HighlightDepthMode
        public const long Enabled = 0xdc;  // bool
        public const long FillColor = 0xb0;  // Color3
        public const long FillTransparency = 0xcc;  // float
        public const long LineThickness = 0xd0;  // int
        public const long OutlineColor = 0xbc;  // Color3
        public const long OutlineTransparency = 0xd4;  // float
        public const long ReservedId = 0xd8;  // Enums::ReservedHighlightId
    }
    public static class HopperBin
    {
        public const long Active = 0x3ec;  // bool
        public const long BinType = 0x3e8;  // Enums::BinTypeEnum::BinType
    }
    public static class HttpService
    {
        public const long HttpEnabled = 0xa1;  // bool
    }
    public static class HumanoidDescription
    {
        public const long BodyTypeScale = 0x130;  // float
        public const long ClimbAnimation = 0xd0;  // int64
        public const long DepthScale = 0x134;  // float
        public const long Face = 0xd8;  // int64
        public const long FallAnimation = 0xe0;  // int64
        public const long GraphicTShirt = 0xe8;  // int64
        public const long HeadScale = 0x138;  // float
        public const long HeightScale = 0x13c;  // float
        public const long IdleAnimation = 0xf0;  // int64
        public const long JumpAnimation = 0xf8;  // int64
        public const long MoodAnimation = 0x100;  // int64
        public const long NumberEmotesLoaded = 0x140;  // int
        public const long Pants = 0x108;  // int64
        public const long ProportionScale = 0x144;  // float
        public const long ResetIncludesBodyParts = 0x14c;  // bool
        public const long RunAnimation = 0x110;  // int64
        public const long Shirt = 0x118;  // int64
        public const long StaticFacialAnimation = 0x14d;  // bool
        public const long SwimAnimation = 0x120;  // int64
        public const long UseAvatarSettings = 0x14e;  // bool
        public const long WalkAnimation = 0x128;  // int64
        public const long WidthScale = 0x148;  // float
    }
    public static class HumanoidRigDescription
    {
        public const long Chest = 0x98;
        public const long ChestRangeMax = 0x648;  // Vector3
        public const long ChestRangeMin = 0x654;  // Vector3
        public const long ChestSize = 0x858;  // float
        public const long ChestTposeAdjustment = 0x1f8;  // CoordinateFrame
        public const long HeadBase = 0xa8;
        public const long HeadBaseRangeMax = 0x660;  // Vector3
        public const long HeadBaseRangeMin = 0x66c;  // Vector3
        public const long HeadBaseSize = 0x85c;  // float
        public const long HeadBaseTposeAdjustment = 0x228;  // CoordinateFrame
        public const long LeftAnkle = 0xb8;
        public const long LeftAnkleRangeMax = 0x678;  // Vector3
        public const long LeftAnkleRangeMin = 0x684;  // Vector3
        public const long LeftAnkleSize = 0x860;  // float
        public const long LeftAnkleTposeAdjustment = 0x258;  // CoordinateFrame
        public const long LeftClavicle = 0xc8;
        public const long LeftClavicleRangeMax = 0x690;  // Vector3
        public const long LeftClavicleRangeMin = 0x69c;  // Vector3
        public const long LeftClavicleSize = 0x864;  // float
        public const long LeftClavicleTposeAdjustment = 0x288;  // CoordinateFrame
        public const long LeftElbow = 0xd8;
        public const long LeftElbowRangeMax = 0x6a8;  // Vector3
        public const long LeftElbowRangeMin = 0x6b4;  // Vector3
        public const long LeftElbowSize = 0x868;  // float
        public const long LeftElbowTposeAdjustment = 0x2b8;  // CoordinateFrame
        public const long LeftHip = 0xe8;
        public const long LeftHipRangeMax = 0x6c0;  // Vector3
        public const long LeftHipRangeMin = 0x6cc;  // Vector3
        public const long LeftHipSize = 0x86c;  // float
        public const long LeftHipTposeAdjustment = 0x2e8;  // CoordinateFrame
        public const long LeftKnee = 0xf8;
        public const long LeftKneeRangeMax = 0x6d8;  // Vector3
        public const long LeftKneeRangeMin = 0x6e4;  // Vector3
        public const long LeftKneeSize = 0x870;  // float
        public const long LeftKneeTposeAdjustment = 0x318;  // CoordinateFrame
        public const long LeftShoulder = 0x108;
        public const long LeftShoulderRangeMax = 0x6f0;  // Vector3
        public const long LeftShoulderRangeMin = 0x6fc;  // Vector3
        public const long LeftShoulderSize = 0x874;  // float
        public const long LeftShoulderTposeAdjustment = 0x348;  // CoordinateFrame
        public const long LeftToeBase = 0x118;
        public const long LeftToeBaseRangeMax = 0x708;  // Vector3
        public const long LeftToeBaseRangeMin = 0x714;  // Vector3
        public const long LeftToeBaseSize = 0x878;  // float
        public const long LeftToeBaseTposeAdjustment = 0x378;  // CoordinateFrame
        public const long LeftWrist = 0x128;
        public const long LeftWristRangeMax = 0x720;  // Vector3
        public const long LeftWristRangeMin = 0x72c;  // Vector3
        public const long LeftWristSize = 0x87c;  // float
        public const long LeftWristTposeAdjustment = 0x3a8;  // CoordinateFrame
        public const long Neck = 0x138;
        public const long NeckRangeMax = 0x738;  // Vector3
        public const long NeckRangeMin = 0x744;  // Vector3
        public const long NeckSize = 0x880;  // float
        public const long NeckTposeAdjustment = 0x3d8;  // CoordinateFrame
        public const long OriginOffset = 0x408;  // CoordinateFrame
        public const long RightAnkle = 0x148;
        public const long RightAnkleRangeMax = 0x750;  // Vector3
        public const long RightAnkleRangeMin = 0x75c;  // Vector3
        public const long RightAnkleSize = 0x884;  // float
        public const long RightAnkleTposeAdjustment = 0x438;  // CoordinateFrame
        public const long RightClavicle = 0x158;
        public const long RightClavicleRangeMax = 0x768;  // Vector3
        public const long RightClavicleRangeMin = 0x774;  // Vector3
        public const long RightClavicleSize = 0x888;  // float
        public const long RightClavicleTposeAdjustment = 0x468;  // CoordinateFrame
        public const long RightElbow = 0x168;
        public const long RightElbowRangeMax = 0x780;  // Vector3
        public const long RightElbowRangeMin = 0x78c;  // Vector3
        public const long RightElbowSize = 0x88c;  // float
        public const long RightElbowTposeAdjustment = 0x498;  // CoordinateFrame
        public const long RightHip = 0x178;
        public const long RightHipRangeMax = 0x798;  // Vector3
        public const long RightHipRangeMin = 0x7a4;  // Vector3
        public const long RightHipSize = 0x890;  // float
        public const long RightHipTposeAdjustment = 0x4c8;  // CoordinateFrame
        public const long RightKnee = 0x188;
        public const long RightKneeRangeMax = 0x7b0;  // Vector3
        public const long RightKneeRangeMin = 0x7bc;  // Vector3
        public const long RightKneeSize = 0x894;  // float
        public const long RightKneeTposeAdjustment = 0x4f8;  // CoordinateFrame
        public const long RightShoulder = 0x198;
        public const long RightShoulderRangeMax = 0x7c8;  // Vector3
        public const long RightShoulderRangeMin = 0x7d4;  // Vector3
        public const long RightShoulderSize = 0x898;  // float
        public const long RightShoulderTposeAdjustment = 0x528;  // CoordinateFrame
        public const long RightToeBase = 0x1a8;
        public const long RightToeBaseRangeMax = 0x7e0;  // Vector3
        public const long RightToeBaseRangeMin = 0x7ec;  // Vector3
        public const long RightToeBaseSize = 0x89c;  // float
        public const long RightToeBaseTposeAdjustment = 0x558;  // CoordinateFrame
        public const long RightWrist = 0x1b8;
        public const long RightWristRangeMax = 0x7f8;  // Vector3
        public const long RightWristRangeMin = 0x804;  // Vector3
        public const long RightWristSize = 0x8a0;  // float
        public const long RightWristTposeAdjustment = 0x588;  // CoordinateFrame
        public const long Root = 0x1c8;
        public const long RootRangeMax = 0x810;  // Vector3
        public const long RootRangeMin = 0x81c;  // Vector3
        public const long RootSize = 0x8a4;  // float
        public const long RootTposeAdjustment = 0x5b8;  // CoordinateFrame
        public const long Spine = 0x1d8;
        public const long SpineRangeMax = 0x828;  // Vector3
        public const long SpineRangeMin = 0x834;  // Vector3
        public const long SpineSize = 0x8a8;  // float
        public const long SpineTposeAdjustment = 0x5e8;  // CoordinateFrame
        public const long Waist = 0x1e8;
        public const long WaistRangeMax = 0x840;  // Vector3
        public const long WaistRangeMin = 0x84c;  // Vector3
        public const long WaistSize = 0x8ac;  // float
        public const long WaistTposeAdjustment = 0x618;  // CoordinateFrame
    }
    public static class IkControl
    {
        public const long ChainRoot = 0xa0;
        public const long Enabled = 0x150;  // bool
        public const long EndEffector = 0xb0;
        public const long Pole = 0xc0;
        public const long Priority = 0x140;  // int
        public const long SmoothTime = 0x144;  // float
        public const long Target = 0xd0;
        public const long Type = 0x148;  // Enums::Type
        public const long Weight = 0x14c;  // float
    }
    public static class ImageHandleAdornment
    {
        public const long DoubleSided = 0x1c0;  // bool
        public const long Size = 0x1b8;  // Vector2
    }
    public static class ImageLabel
    {
        public const long ImageColor3 = 0xac0;  // Color3; heuristic decode, passed live check
    }
    public static class IncrementalPatchBuilder
    {
        public const long AddPathsToBundle = 0xb0;  // bool
        public const long BuildDebouncePeriod = 0x170;  // double
        public const long HighCompression = 0xb1;  // bool
        public const long SerializePatch = 0xb2;  // bool
        public const long UseFileLevelCompressionInsteadOfChunk = 0xb3;  // bool
        public const long ZstdCompression = 0xb4;  // bool
    }
    public static class InputAction
    {
        public const long DisplayName = 0xa0;
        public const long Enabled = 0xec;  // bool
        public const long Type = 0xe8;  // Enums::InputActionType
    }
    public static class InputBinding
    {
        public const long Backward = 0x11c;  // KeyCode
        public const long ClampMagnitudeToOne = 0x158;  // bool
        public const long Deadzone = 0x10c;  // NumberRange
        public const long DisplayName = 0xc8;
        public const long Down = 0x120;  // KeyCode
        public const long Forward = 0x124;  // KeyCode
        public const long KeyCode = 0x128;  // KeyCode
        public const long Left = 0x12c;  // KeyCode
        public const long PointerIndex = 0x130;  // int
        public const long PressedThreshold = 0x134;  // float
        public const long PrimaryModifier = 0x138;  // KeyCode
        public const long ResponseCurve = 0x140;  // float
        public const long Right = 0x144;  // KeyCode
        public const long Scale = 0x148;  // float
        public const long SecondaryModifier = 0x14c;  // KeyCode
        public const long Type = 0x150;  // Enums::InputBindingType
        public const long Up = 0x154;  // KeyCode
        public const long Vector2Scale = 0x114;  // Vector2
        public const long Vector3Scale = 0x100;  // Vector3
    }
    public static class InputContext
    {
        public const long Enabled = 0xa4;  // bool
        public const long Priority = 0xa0;  // int
        public const long Sink = 0xa5;  // bool
    }
    public static class InputObject
    {
        public const long Delta = 0xa0;  // Vector3
        public const long KeyCode = 0xac;  // KeyCode
        public const long UserInputState = 0xb0;  // Enums::UserInputStateEnum::UserInputState
        public const long UserInputType = 0xb4;  // Enums::UserInputTypeEnum::UserInputType
    }
    public static class InsertService
    {
        public const long AllowInsertFreeModels = 0xa1;  // bool
    }
    public static class IntConstrainedValue
    {
        public const long MaxValue = 0xa0;  // int64
        public const long MinValue = 0xa8;  // int64
    }
    public static class IntValue
    {
        public const long Value = 0xa0;  // int64
    }
    public static class JointInstance
    {
        public const long Enabled = 0xa0;  // bool
    }
    public static class Keyframe
    {
        public const long Time = 0xa0;  // float
    }
    public static class KeyframeMarker
    {
        public const long Value = 0xa0;
    }
    public static class KeyframeSequence
    {
        public const long AuthoredHipHeight = 0xc0;  // float
    }
    public static class Light
    {
        public const long Brightness = 0xb4;  // float
        public const long Color = 0xa8;  // Color3
        public const long Enabled = 0xb8;  // bool
        public const long Shadows = 0xb9;  // bool
    }
    public static class Lighting
    {
        public const long Ambient = 0xb8;  // Color3
        public const long Brightness = 0x100;  // float
        public const long ClockTime = 0xb0;  // float; heuristic decode, passed live check
        public const long ColorShift_Bottom = 0xc4;  // Color3
        public const long ColorShift_Top = 0xd0;  // Color3
        public const long EnvironmentDiffuseScale = 0x104;  // float
        public const long EnvironmentSpecularScale = 0x108;  // float
        public const long ExposureCompensation = 0x10c;  // float
        public const long ExtendLightRangeTo120 = 0x110;  // Enums::RolloutState
        public const long FogColor = 0xdc;  // Color3
        public const long FogEnd = 0x114;  // float
        public const long FogStart = 0x118;  // float
        public const long GeographicLatitude = 0x11c;  // float
        public const long GlobalShadows = 0x12c;  // bool
        public const long LightingStyle = 0x120;  // LightingStyle
        public const long OutdoorAmbient = 0xe8;  // Color3
        public const long Outlines = 0x12d;  // bool
        public const long PrioritizeLightingQuality = 0x12e;  // bool
        public const long ShadowColor = 0xf4;  // Color3
        public const long ShadowSoftness = 0x124;  // float
    }
    public static class LineHandleAdornment
    {
        public const long Length = 0x18c;  // float
        public const long Thickness = 0x190;  // float
    }
    public static class LocalizationService
    {
        public const long ForcePlayModeGameLocaleId = 0xb0;
        public const long ForcePlayModeRobloxLocaleId = 0xc8;
        public const long GameSourceLanguageId = 0xe0;
        public const long IsImageCaptureEnabled = 0x108;  // bool
        public const long RobloxForcePlayModeGameLocaleId = 0xb0;
        public const long RobloxForcePlayModeRobloxLocaleId = 0xc8;
        public const long ShouldUseCloudTable = 0x109;  // bool
        public const long ShouldUseImageLocalizationTable = 0x10a;  // bool
    }
    public static class LocalizationTable
    {
        public const long DevelopmentLanguage = 0xa0;
        public const long IsExemptFromUGCAnalytics = 0xc8;  // bool
        public const long SourceLocaleId = 0xa0;
    }
    public static class LodDataEntity
    {
        public const long EntityLodEnabled = 0x134;  // bool
        public const long EntityModelSize = 0x118;  // Vector3
        public const long EntityPosition = 0xe8;  // CoordinateFrame
        public const long EntityScale = 0x124;  // Vector3
        public const long EntityVisible = 0x135;  // bool
        public const long IsSlimEnabled = 0x136;  // bool
        public const long SlimReplicationTimestampSec = 0xe0;  // double
        public const long TranscoderFailureReason = 0xa0;
        public const long TranscoderStatus = 0x130;  // SlimTranscoderStatus
    }
    public static class LuaSourceContainer
    {
        public const long CachedRemoteSource = 0xa0;  // ProtectedString
        public const long CachedRemoteSourceLoadState = 0xd0;  // int
        public const long HasAssociatedDrafts = 0xd4;  // bool
        public const long IsDifferentFromFileSystem = 0xd5;  // bool
        public const long ScriptGuid = 0xb8;
        public const long isPlayerScript = 0xd6;  // bool
    }
    public static class MakeupDescription
    {
        public const long AssetId = 0xa8;  // int64
        public const long Instance = 0x98;
        public const long MakeupType = 0xb0;  // MakeupType
        public const long Order = 0xb4;  // int
    }
    public static class MaterialService
    {
        public const long Use2022Materials = 0x478;  // bool
        public const long Use2022MaterialsXml = 0x478;  // bool
    }
    public static class MaterialVariant
    {
        public const long AlphaMode = 0x1b8;  // TexturePackAlphaMode
        public const long AvgMetalness = 0x1bc;  // int
        public const long AvgRoughness = 0x1c0;  // int
        public const long BaseMaterial = 0x1c4;  // MaterialType
        public const long ColorMapContent = 0xa0;  // Content
        public const long EmissiveMaskContent = 0xc8;  // Content
        public const long EmissiveStrength = 0x1c8;  // float
        public const long EmissiveTint = 0x1ac;  // Color3
        public const long MaterialPattern = 0x1cc;  // MaterialPattern
        public const long MetalnessMapContent = 0xf0;  // Content
        public const long NormalMapContent = 0x118;  // Content
        public const long RoughnessMapContent = 0x140;  // Content
        public const long StudsPerTile = 0x1d0;  // float
    }
    public static class MegaClusterInstance
    {
        public const long AcquisitionMethod = 0x1c4;  // Enums::TerrainAcquisitionMethodEnum::TerrainAcquisitionMethod
        public const long Decoration = 0x1e0;  // bool
        public const long ExpandedTerrainResolved = 0x1e1;  // bool
        public const long GrassLength = 0x1c8;  // float
        public const long LastUsedModificationMethod = 0x1cc;  // Enums::TerrainAcquisitionMethodEnum::TerrainAcquisitionMethod
        public const long SmoothVoxelsUpgraded = 0x1e2;  // bool
        public const long WaterColor = 0x1b8;  // Color3
        public const long WaterReflectance = 0x1d0;  // float
        public const long WaterTransparency = 0x1d4;  // float
        public const long WaterWaveSize = 0x1d8;  // float
        public const long WaterWaveSpeed = 0x1dc;  // float
    }
    public static class MeshPart
    {
        public const long DoubleSided = 0x33c;  // bool
        public const long HasJointOffset = 0x33d;  // bool
        public const long HasSkinnedMesh = 0x33e;  // bool
        public const long JointOffset = 0x328;  // Vector3
        public const long MeshContent = 0x2d0;  // Content
        public const long RenderFidelity = 0x334;  // RenderFidelity
        public const long RenderFidelityReplicate = 0x334;  // RenderFidelity
        public const long TextureContent = 0x2f8;  // Content
        public const long VertexCount = 0x338;  // int
    }
    public static class Message
    {
        public const long Text = 0xa0;
    }
    public static class MicroProfilerService
    {
        public const long ContextLabel = 0xa8;
    }
    public static class ModelInstance
    {
        public const long LevelOfDetail = 0x11c;  // ModelLevelOfDetail
        public const long ModelMeshCFrame = 0xe0;  // CoordinateFrame
        public const long ModelMeshData = 0xc8;  // SharedString
        public const long ModelMeshSize = 0x110;  // Vector3
        public const long ModelStreamingMode = 0x120;  // ModelStreamingMode
        public const long Scale = 0x124;  // float
        public const long ScaleFactor = 0x124;  // float
        public const long SlimHash = 0xd0;  // SharedString
        public const long WorldPivotData = 0xd8;  // OptionalCoordinateFrame
    }
    public static class ModuleScript
    {
        public const long LinkedSource = 0xe8;  // ContentId
        public const long Source = 0x108;  // ProtectedString
    }
    public static class Motor6D
    {
        public const long EnableSkinning = 0x198;  // bool
    }
    public static class NegateOperation
    {
        public const long PreviousOperation = 0x3c0;  // NegateOperationHiddenHistory
    }
    public static class Noise
    {
        public const long NoiseType = 0x98;  // NoiseType
        public const long Seed = 0x9c;  // int
    }
    public static class NotificationService
    {
        public const long SelectedTheme = 0xa8;
    }
    public static class PackageLink
    {
        public const long AutoUpdate = 0x10c;  // bool
        public const long CanAutoUpdate = 0x10d;  // bool
        public const long DefaultName = 0xc8;
        public const long HasNewVersion = 0x10e;  // bool
        public const long ModifiedState = 0x108;  // int
        public const long PackageContentSerialize = 0xa0;  // Content
        public const long PackageGuid = 0xf8;  // int64
        public const long SerializedDefaultAttributes = 0xe0;  // BinaryString
    }
    public static class Packages
    {
        public const long IsDehydrated = 0xac;  // bool
        public const long OverridesRecalculated = 0xad;  // bool
        public const long ShellPackagesCount = 0xa4;  // int
        public const long SkippedInstancesCount = 0xa8;  // int
    }
    public static class ParabolaAdornment
    {
        public const long A = 0xe8;  // float
        public const long B = 0xec;  // float
        public const long C = 0xf0;  // float
        public const long Range = 0xf4;  // float
        public const long Thickness = 0xf8;  // float
    }
    public static class PartOperation
    {
        public const long ChildData = 0x2f8;  // BinaryString
        public const long ChildData2 = 0x348;  // SharedString
        public const long ComponentIndex = 0x360;  // int
        public const long DCDPropertyData = 0x310;  // CSGPropertyData
        public const long MeshData = 0x328;  // BinaryString
        public const long MeshData2 = 0x358;  // SharedString
        public const long OffCentered = 0x374;  // bool
        public const long RenderFidelity = 0x368;  // RenderFidelity
        public const long SmoothingAngle = 0x36c;  // float
        public const long UsePartColor = 0x375;  // bool
    }
    public static class PartOperationAsset
    {
        public const long MeshData = 0xb0;  // BinaryString
    }
    public static class ParticleEmitter2D
    {
        public const long Acceleration = 0x1d8;  // Vector2
        public const long Blend = 0x218;  // float
        public const long Brightness = 0x21c;  // float
        public const long Drag = 0x220;  // float
        public const long EmissionAngle = 0x224;  // float
        public const long EmissionMode = 0x228;  // ParticleEmitter2DEmissionMode
        public const long EmissionOffset = 0x1e0;  // Vector2
        public const long EmissionSpread = 0x1e8;  // Vector2
        public const long Enabled = 0x250;  // bool
        public const long FlipbookBlendFrames = 0x251;  // bool
        public const long FlipbookFramerate = 0x1f0;  // NumberRange
        public const long FlipbookLayout = 0x22c;  // ParticleFlipbookLayout
        public const long FlipbookMode = 0x230;  // ParticleFlipbookMode
        public const long FlipbookSizeX = 0x234;  // int
        public const long FlipbookSizeY = 0x238;  // int
        public const long FlipbookStartRandom = 0x252;  // bool
        public const long Lifetime = 0x1f8;  // NumberRange
        public const long LightEmission = 0x23c;  // float
        public const long LockedToParent = 0x253;  // bool
        public const long Rate = 0x240;  // float
        public const long RotSpeed = 0x200;  // NumberRange
        public const long Rotation = 0x208;  // NumberRange
        public const long Speed = 0x210;  // NumberRange
        public const long SpreadAngle = 0x244;  // float
        public const long TimeScale = 0x248;  // float
        public const long ZIndex = 0x24c;  // int
    }
    public static class PatchMapping
    {
        public const long FlattenTree = 0xc8;  // bool
        public const long PatchId = 0x98;
        public const long TargetPath = 0xb0;
    }
    public static class Path2D
    {
        public const long SelectedControlPoint = 0xd4;  // int
        public const long Transparency = 0xdc;  // float
    }
    public static class PathfindingLink
    {
        public const long IsBidirectional = 0xd8;  // bool
        public const long Label = 0xa0;
    }
    public static class PathfindingModifier
    {
        public const long Label = 0xa0;
        public const long PassThrough = 0xb8;  // bool
    }
    public static class PhysicsActivitySensor
    {
        public const long Position = 0x228;  // Vector3
        public const long Size = 0x234;  // Vector3
    }
    public static class PlayerDataService
    {
        public const long LoadFailureBehavior = 0xa4;  // Enums::PlayerDataLoadFailureBehavior
    }
    public static class PlayerEmulatorService
    {
        public const long CustomPoliciesEnabled = 0xfc;  // bool
        public const long EmulatedCountryCode = 0xb0;
        public const long EmulatedGameLocale = 0xc8;
        public const long PlayerEmulationEnabled = 0xfd;  // bool
        public const long PseudolocalizationEnabled = 0xfe;  // bool
        public const long SerializedEmulatedPolicyInfo = 0xe0;  // BinaryString
        public const long TextElongationFactor = 0xf8;  // int
    }
    public static class PlayerGui
    {
        public const long InputBindingMappingsRaw = 0x148;  // BinaryString
        public const long ScreenOrientation = 0x174;  // Enums::ScreenOrientationEnum::ScreenOrientation
    }
    public static class PlayerListConfiguration
    {
        public const long Open = 0x96;  // bool
    }
    public static class Plugin
    {
        public const long DisableUIDragDetectorDrags = 0xc4;  // bool
        public const long IsDebuggable = 0xc5;  // bool
        public const long UsesAssetInsertionDrag = 0xc6;  // bool
    }
    public static class PluginAction
    {
        public const long Checked = 0x100;  // bool
        public const long DefaultShortcut = 0xd0;
        public const long Enabled = 0x101;  // bool
        public const long Text = 0xe8;
        public const long Visible = 0x102;  // bool
    }
    public static class PluginCapabilities
    {
        public const long Manifest = 0x98;
    }
    public static class PluginGui
    {
        public const long Title = 0x770;
    }
    public static class PluginMenu
    {
        public const long Icon = 0xd0;
        public const long Title = 0xe8;
        public const long Visible = 0x100;  // bool
    }
    public static class PluginToolbarButton
    {
        public const long ClickableWhenViewportHidden = 0x100;  // bool
        public const long Enabled = 0x101;  // bool
    }
    public static class PointLight
    {
        public const long Range = 0xbc;  // float
    }
    public static class PolicyService
    {
        public const long IsLuobuServer = 0xa4;  // Enums::TriStateBoolean
        public const long LuobuWhitelisted = 0xa8;  // Enums::TriStateBoolean
    }
    public static class PoseBase
    {
        public const long EasingDirection = 0xa0;  // Pose::PoseEasingDirection
        public const long EasingStyle = 0xa4;  // Pose::PoseEasingStyle
        public const long Weight = 0xa8;  // float
    }
    public static class PostEffect
    {
        public const long Enabled = 0x95;  // bool
    }
    public static class ProceduralModel
    {
        public const long Dirty = 0x324;  // bool
        public const long Size = 0x318;  // Vector3
    }
    public static class ProximityPrompt
    {
        public const long ActionText = 0x98;
        public const long AutoLocalize = 0x10c;  // bool
        public const long ClickablePrompt = 0x10d;  // bool
        public const long Enabled = 0x10e;  // bool
        public const long Exclusivity = 0xf0;  // Enums::ProximityPromptExclusivityEnum::ProximityPromptExclusivity
        public const long GamepadKeyCode = 0xf4;  // KeyCode
        public const long HoldDuration = 0xf8;  // float
        public const long KeyboardKeyCode = 0xfc;  // KeyCode
        public const long MaxActivationDistance = 0x100;  // float
        public const long MaxIndicatorDistance = 0x104;  // float
        public const long ObjectText = 0xb0;
        public const long RequiresLineOfSight = 0x10f;  // bool
        public const long Style = 0x108;  // Enums::ProximityPromptStyleEnum::ProximityPromptStyle
        public const long UIOffset = 0xe8;  // Vector2
    }
    public static class ProximityPromptService
    {
        public const long Enabled = 0xc0;  // bool
        public const long MaxIndicatorsVisible = 0xb8;  // int
        public const long MaxPromptsVisible = 0xbc;  // int
    }
    public static class PyramidHandleAdornment
    {
        public const long DoubleSided = 0x19c;  // bool
        public const long Height = 0x18c;  // float
        public const long Shading = 0x190;  // Enums::AdornShading
        public const long Sides = 0x194;  // int
        public const long Size = 0x198;  // float
    }
    public static class RVideo_VideoDeviceInput
    {
        public const long Active = 0x170;  // bool
        public const long CameraId = 0x170;
        public const long CaptureQuality = 0x180;
    }
    public static class RealTimeAnimation_RTAnimationTracker
    {
        public const long Active = 0x11c;  // bool
        public const long EnableFallbackAudioInput = 0x11d;  // bool
        public const long SessionName = 0xf0;
        public const long TrackerType = 0x118;
    }
    public static class RealtimeMedia
    {
        public const long ForwardInput = 0x131;  // bool
    }
    public static class RenderingTest
    {
        public const long CFrame = 0xd8;  // CoordinateFrame
        public const long ComparisonDiffThreshold = 0x1c0;  // int
        public const long ComparisonMethod = 0x1c8;  // RenderingTestComparisonMethod
        public const long ComparisonPsnrThreshold = 0x1c4;  // float
        public const long Description = 0xa0;
        public const long FieldOfView = 0x108;  // float
        public const long PerfTest = 0x114;  // bool
        public const long Position = 0xfc;  // Vector3
        public const long QualityAuto = 0x1b8;  // bool
        public const long QualityLevel = 0x1bc;  // int
        public const long RenderingTestFrameCount = 0x10c;  // int
        public const long ShouldSkip = 0x115;  // bool
        public const long Ticket = 0xb8;
        public const long Timeout = 0x110;  // int
    }
    public static class RobloxSerializableInstance
    {
        public const long Data = 0x98;  // BinaryString
    }
    public static class Rocket
    {
        public const long Active = 0x2c0;  // bool
        public const long CartoonFactor = 0x2a0;  // float
        public const long MaxSpeed = 0x2a4;  // float
        public const long MaxThrust = 0x2a8;  // float
        public const long MaxTorque = 0x288;  // Vector3
        public const long Target = 0x278;
        public const long TargetOffset = 0x294;  // Vector3
        public const long TargetRadius = 0x2ac;  // float
        public const long ThrustD = 0x2b0;  // float
        public const long ThrustP = 0x2b4;  // float
        public const long TurnD = 0x2b8;  // float
        public const long TurnP = 0x2bc;  // float
    }
    public static class RolloutValidation
    {
        public const long AdditionalFluffOne = 0x188;  // int
        public const long AdditionalFluffThree = 0x18c;  // float
        public const long AdditionalFluffTwo = 0x318;  // bool
        public const long CreationVersion = 0x190;  // int
        public const long FirstBinaryString = 0xb0;  // BinaryString
        public const long FirstSharedExpectedValue = 0xc8;
        public const long FirstSharedString = 0x170;  // SharedString
        public const long GenerationStrategy = 0x194;  // int
        public const long SecondBinaryExpectedValue = 0xe0;
        public const long SecondBinaryString = 0xf8;  // BinaryString
        public const long SecondSharedExpectedValue = 0x110;
        public const long SecondSharedString = 0x178;  // SharedString
        public const long ThirdBinaryExpectedValue = 0x128;
        public const long ThirdBinaryString = 0x140;  // BinaryString
        public const long ThirdSharedExpectedValue = 0x158;
        public const long ThirdSharedString = 0x180;  // SharedString
    }
    public static class RunService
    {
        public const long RunState = 0xc0;  // RunState
    }
    public static class Safety_SafetyService
    {
        public const long IsCaptureModeForReport = 0xa1;  // bool
    }
    public static class ScreenGui
    {
        public const long ClipToDeviceSafeArea = 0x6a4;  // bool
        public const long DisplayOrder = 0x698;  // int
        public const long IgnoresTitleBarReservation = 0x6a5;  // bool
        public const long OnTopOfCoreBlur = 0x6a6;  // bool
        public const long SafeAreaCompatibility = 0x69c;  // SafeAreaCompatMode
        public const long ScreenInsets = 0x6a0;  // ScreenInsetsType
    }
    public static class ScreenshotHud
    {
        public const long CameraButtonPosition = 0xc0;  // UDim2
        public const long CloseButtonPosition = 0xd0;  // UDim2
        public const long CloseWhenScreenshotTaken = 0xe4;  // bool
        public const long ExperienceNameOverlayEnabled = 0xe5;  // bool
        public const long HideCoreGuiForCaptures = 0xe6;  // bool
        public const long HidePlayerGuiForCaptures = 0xe7;  // bool
        public const long OverlayFont = 0xe0;  // Text::Font
        public const long UsernameOverlayEnabled = 0xe8;  // bool
        public const long Visible = 0xe9;  // bool
    }
    public static class Script
    {
        public const long Source = 0x160;  // ProtectedString
    }
    public static class ScriptContext
    {
        public const long ScriptsDisabled = 0xa1;  // bool
    }
    public static class Scripting_DebuggerBreakpoint
    {
        public const long ContinueExecution = 0xa4;  // bool
        public const long IsEnabled = 0xa5;  // bool
        public const long isContextDependentBreakpoint = 0xa6;  // bool
    }
    public static class ScrollingFrame
    {
        public const long CanvasPosition = 0xa64;  // Vector2
        public const long ScrollBarImageColor3 = 0xa50;  // Color3; heuristic decode, passed live check
        public const long ScrollRate = 0xa94;  // float
        public const long SmoothScroll = 0xaa5;  // bool
    }
    public static class Selection
    {
        public const long ShowActiveInstanceHighlight = 0xb4;  // bool
    }
    public static class SelectionBox
    {
        public const long LineThickness = 0xfc;  // float
        public const long StudioSelectionBox = 0x104;  // bool
        public const long SurfaceColor = 0xf0;  // BrickColor
        public const long SurfaceColor3 = 0xf0;  // Color3
        public const long SurfaceTransparency = 0x100;  // float
    }
    public static class SelectionPointLasso
    {
        public const long Point = 0xf0;  // Vector3
    }
    public static class SelectionSphere
    {
        public const long SurfaceColor = 0xf0;  // BrickColor
        public const long SurfaceColor3 = 0xf0;  // Color3
        public const long SurfaceTransparency = 0xfc;  // float
    }
    public static class SelfViewConfiguration
    {
        public const long Open = 0x96;  // bool
    }
    public static class SensorBase
    {
        public const long UpdateType = 0x98;  // SensorUpdateType
    }
    public static class ServerScriptService
    {
        public const long LoadStringEnabled = 0xb0;  // bool
    }
    public static class ShirtGraphic
    {
        public const long Color3 = 0xd0;  // Color3
    }
    public static class SkateboardPlatform
    {
        public const long MoveState = 0x200;  // Enums::MoveStateEnum::MoveState
        public const long Steer = 0x204;  // int
        public const long StickyWheels = 0x20c;  // bool
        public const long Throttle = 0x208;  // int
    }
    public static class Skin
    {
        public const long SkinColor = 0xa8;  // BrickColor
    }
    public static class Sky
    {
        public const long CelestialBodiesShown = 0x1f8;  // bool
        public const long MoonAngularSize = 0x1ec;  // float
        public const long SkyboxOrientation = 0x1e0;  // Vector3
        public const long StarCount = 0x1f0;  // int
        public const long SunAngularSize = 0x1f4;  // float
    }
    public static class SlimAnimationDataEntity
    {
        public const long BoneParentIndices = 0x98;  // BinaryString
        public const long EntityScale = 0xd8;  // double
        public const long Handle = 0xe8;  // int
        public const long IsSlimEnabled = 0xf4;  // bool
        public const long NumBones = 0xec;  // int
        public const long RootIndex = 0xf0;  // int
        public const long SlimInstanceHashes = 0xb0;  // BinaryString
        public const long SlimReplicationTimestampSec = 0xe0;  // double
    }
    public static class Smoke
    {
        public const long Color = 0xa0;  // Color3
        public const long Enabled = 0xc0;  // bool
        public const long LocalTransparencyModifier = 0xac;  // float
        public const long Opacity = 0xb0;  // float
        public const long RiseVelocity = 0xb4;  // float
        public const long Size = 0xb8;  // float
        public const long TimeScale = 0xbc;  // float
        public const long opacity_xml = 0xb0;  // float
        public const long riseVelocity_xml = 0xb4;  // float
        public const long size_xml = 0xb8;  // float
    }
    public static class Soundscape_AudioAnalyzer
    {
        public const long SpectrumEnabled = 0x124;  // bool
        public const long WindowSize = 0x120;
    }
    public static class Soundscape_AudioChannelMixer
    {
        public const long Layout = 0x120;  // Enums::AudioChannelLayout
    }
    public static class Soundscape_AudioChannelSplitter
    {
        public const long Layout = 0x120;  // Enums::AudioChannelLayout
    }
    public static class Soundscape_AudioChorus
    {
        public const long Bypass = 0x12c;  // bool
        public const long Depth = 0x120;  // float
        public const long Mix = 0x124;  // float
        public const long Rate = 0x128;  // float
    }
    public static class Soundscape_AudioCompressor
    {
        public const long Attack = 0x120;  // float
        public const long Bypass = 0x134;  // bool
        public const long MakeupGain = 0x124;  // float
        public const long Ratio = 0x128;  // float
        public const long Release = 0x12c;  // float
        public const long Threshold = 0x130;  // float
    }
    public static class Soundscape_AudioDeviceInput
    {
        public const long AccessType = 0x158;
        public const long Active = 0x160;  // bool
        public const long DictationEnabled = 0x161;  // bool
        public const long EchoCancellation = 0x162;  // bool
        public const long GainControl = 0x163;  // bool
        public const long Muted = 0x164;  // bool
        public const long MutedByLocalUser = 0x165;  // bool
        public const long NoiseSuppression = 0x166;  // bool
        public const long Streaming = 0x167;  // bool
        public const long Volume = 0x15c;  // float
    }
    public static class Soundscape_AudioDistortion
    {
        public const long Bypass = 0x124;  // bool
        public const long Level = 0x120;  // float
    }
    public static class Soundscape_AudioEcho
    {
        public const long Bypass = 0x134;  // bool
        public const long DelayTime = 0x120;  // float
        public const long DryLevel = 0x124;  // float
        public const long Feedback = 0x128;  // float
        public const long RampTime = 0x12c;  // float
        public const long WetLevel = 0x130;  // float
    }
    public static class Soundscape_AudioEmitter
    {
        public const long AcousticSimulationEnabled = 0x168;  // bool
        public const long AudioInteractionGroup = 0x138;
        public const long DiffractionEnabled = 0x150;  // Enums::SimulationMode
        public const long DistanceAttenuationBounds = 0x148;  // NumberRange
        public const long DistanceAttenuationMode = 0x154;
        public const long OcclusionEnabled = 0x158;  // Enums::SimulationMode
        public const long PositionType = 0x15c;  // Enums::EmitterPositionType
        public const long ReverbEnabled = 0x160;  // Enums::SimulationMode
        public const long SimulationFidelity = 0x164;  // Enums::AudioSimulationFidelity
    }
    public static class Soundscape_AudioEqualizer
    {
        public const long Bypass = 0x134;  // bool
        public const long HighGain = 0x128;  // float
        public const long LowGain = 0x12c;  // float
        public const long MidGain = 0x130;  // float
        public const long MidRange = 0x120;  // NumberRange
    }
    public static class Soundscape_AudioFader
    {
        public const long Bypass = 0x124;  // bool
        public const long Volume = 0x120;  // float
    }
    public static class Soundscape_AudioFilter
    {
        public const long Bypass = 0x130;  // bool
        public const long FilterType = 0x120;
        public const long Frequency = 0x124;  // float
        public const long Gain = 0x128;  // float
        public const long Q = 0x12c;  // float
    }
    public static class Soundscape_AudioFlanger
    {
        public const long Bypass = 0x12c;  // bool
        public const long Depth = 0x120;  // float
        public const long Mix = 0x124;  // float
        public const long Rate = 0x128;  // float
    }
    public static class Soundscape_AudioGate
    {
        public const long Attack = 0x128;  // float
        public const long Bypass = 0x130;  // bool
        public const long Release = 0x12c;  // float
        public const long Threshold = 0x120;  // NumberRange
    }
    public static class Soundscape_AudioLimiter
    {
        public const long Bypass = 0x128;  // bool
        public const long MaxLevel = 0x120;  // float
        public const long Release = 0x124;  // float
    }
    public static class Soundscape_AudioListener
    {
        public const long AcousticSimulationEnabled = 0x15c;  // bool
        public const long AudioInteractionGroup = 0x138;
        public const long DiffractionEnabled = 0x148;  // Enums::SimulationMode
        public const long OcclusionEnabled = 0x14c;  // Enums::SimulationMode
        public const long PositionType = 0x150;  // Enums::ListenerPositionType
        public const long ReverbEnabled = 0x154;  // Enums::SimulationMode
        public const long SimulationFidelity = 0x158;  // Enums::AudioSimulationFidelity
    }
    public static class Soundscape_AudioPitchShifter
    {
        public const long Bypass = 0x128;  // bool
        public const long Pitch = 0x120;  // float
        public const long WindowSize = 0x124;
    }
    public static class Soundscape_AudioPlayer
    {
        public const long Asset = 0x128;  // ContentId
        public const long AssetRepresentation = 0x150;  // AssetRepresentation
        public const long AudioContent = 0x128;  // Content
        public const long AutoLoad = 0x158;  // bool
        public const long AutoPlay = 0x159;  // bool
        public const long IsPlaying = 0x15a;  // bool
        public const long LoopRegion = 0x140;  // NumberRange
        public const long Looping = 0x15b;  // bool
        public const long PlaybackRegion = 0x148;  // NumberRange
        public const long PlaybackSpeed = 0x130;  // double
        public const long TimePosition = 0x138;  // double
        public const long Volume = 0x154;  // float
    }
    public static class Soundscape_AudioRecorder
    {
        public const long IsRecording = 0x120;  // bool
    }
    public static class Soundscape_AudioReverb
    {
        public const long Bypass = 0x150;  // bool
        public const long DecayRatio = 0x120;  // float
        public const long DecayTime = 0x124;  // float
        public const long Density = 0x128;  // float
        public const long Diffusion = 0x12c;  // float
        public const long DryLevel = 0x130;  // float
        public const long EarlyDelayTime = 0x134;  // float
        public const long HighCutFrequency = 0x138;  // float
        public const long LateDelayTime = 0x13c;  // float
        public const long LowShelfFrequency = 0x140;  // float
        public const long LowShelfGain = 0x144;  // float
        public const long ReferenceFrequency = 0x148;  // float
        public const long WetLevel = 0x14c;  // float
    }
    public static class Soundscape_AudioSpeechToText
    {
        public const long DictationEnabled = 0x168;  // bool
        public const long DisableVoiceDetection = 0x169;  // bool
        public const long EnableVolumeCheck = 0x16a;  // bool
        public const long Enabled = 0x16b;  // bool
        public const long Locale = 0x120;
        public const long Streaming = 0x16c;  // bool
        public const long Text = 0x138;
        public const long UsageType = 0x150;
        public const long VoiceDetectedOverride = 0x16e;  // bool
    }
    public static class Soundscape_AudioTextToSpeech
    {
        public const long AutoLocalize = 0x168;  // bool
        public const long IsPlaying = 0x169;  // bool
        public const long Looping = 0x16a;  // bool
        public const long Pitch = 0x158;  // float
        public const long PlaybackSpeed = 0x15c;  // float
        public const long Speed = 0x160;  // float
        public const long Text = 0x120;
        public const long TimePosition = 0x150;  // double
        public const long VoiceId = 0x138;
        public const long Volume = 0x164;  // float
    }
    public static class Soundscape_AudioTremolo
    {
        public const long Bypass = 0x138;  // bool
        public const long Depth = 0x120;  // float
        public const long Duty = 0x124;  // float
        public const long Frequency = 0x128;  // float
        public const long Shape = 0x12c;  // float
        public const long Skew = 0x130;  // float
        public const long Square = 0x134;  // float
    }
    public static class Soundscape_AudioWindSynthesizer
    {
        public const long Enabled = 0x134;  // bool
        public const long PositionType = 0x128;
        public const long Profile = 0x12c;
        public const long Volume = 0x130;  // float
    }
    public static class Soundscape_ChannelSelectorSoundEffect
    {
        public const long Channel = 0xe8;  // int
    }
    public static class Soundscape_ChorusSoundEffect
    {
        public const long Depth = 0xe0;  // float
        public const long Mix = 0xe4;  // float
        public const long Rate = 0xe8;  // float
    }
    public static class Soundscape_CompressorSoundEffect
    {
        public const long Attack = 0xf0;  // float
        public const long GainMakeup = 0xf4;  // float
        public const long Ratio = 0xf8;  // float
        public const long Release = 0xfc;  // float
        public const long Threshold = 0x100;  // float
    }
    public static class Soundscape_DistortionSoundEffect
    {
        public const long Level = 0xe0;  // float
    }
    public static class Soundscape_EchoSoundEffect
    {
        public const long Delay = 0xe0;  // float
        public const long DryLevel = 0xe4;  // float
        public const long Feedback = 0xe8;  // float
        public const long WetLevel = 0xec;  // float
    }
    public static class Soundscape_EqualizerSoundEffect
    {
        public const long HighGain = 0xe0;  // float
        public const long LowGain = 0xe4;  // float
        public const long MidGain = 0xe8;  // float
    }
    public static class Soundscape_FlangeSoundEffect
    {
        public const long Depth = 0xe0;  // float
        public const long Mix = 0xe4;  // float
        public const long Rate = 0xe8;  // float
    }
    public static class Soundscape_PitchShiftSoundEffect
    {
        public const long Octave = 0xe0;  // float
    }
    public static class Soundscape_ReverbSoundEffect
    {
        public const long DecayTime = 0xe0;  // float
        public const long Density = 0xe4;  // float
        public const long Diffusion = 0xe8;  // float
        public const long DryLevel = 0xec;  // float
        public const long WetLevel = 0xf0;  // float
    }
    public static class Soundscape_Sound
    {
        public const long AcousticSimulationEnabled = 0x11c;  // bool
        public const long AssetRepresentation = 0xe8;  // AssetRepresentation
        public const long EmitterSize = 0x104;  // float
        public const long LoopRegion = 0xd8;  // NumberRange
        public const long Looped = 0x11d;  // bool
        public const long MaxDistance = 0x100;  // float
        public const long MinDistance = 0x104;  // float
        public const long Pitch = 0xfc;  // float
        public const long PlayOnRemove = 0x11e;  // bool
        public const long PlaybackRegion = 0xe0;  // NumberRange
        public const long PlaybackRegionsEnabled = 0x11f;  // bool
        public const long PlaybackSpeed = 0xfc;  // float
        public const long Playing = 0x120;  // bool
        public const long PlayingReplicator = 0x120;  // bool
        public const long RollOffMaxDistance = 0x100;  // float
        public const long RollOffMinDistance = 0x104;  // float
        public const long RollOffMode = 0x108;
        public const long UsageContextPermission = 0x10c;  // UsageContext
        public const long Volume = 0x110;  // float
        public const long xmlRead_MaxDistance_3 = 0x100;  // float
        public const long xmlRead_MinDistance_3 = 0x104;  // float
    }
    public static class Soundscape_SoundEffect
    {
        public const long Enabled = 0xa4;  // bool
        public const long Priority = 0xa0;  // int
    }
    public static class Soundscape_SoundGroup
    {
        public const long Volume = 0xa0;  // float
    }
    public static class Soundscape_SoundService
    {
        public const long AcousticSimulationEnabled = 0x160;  // bool
        public const long AmbientReverb = 0x138;
        public const long AudioApiByDefault = 0x13c;  // Enums::RolloutState
        public const long CharacterSoundsUseNewApi = 0x140;  // Enums::RolloutState
        public const long DefaultListenerLocation = 0x148;
        public const long DiffractionEnabled = 0x161;  // bool
        public const long DistanceFactor = 0x14c;  // float
        public const long DopplerScale = 0x150;  // float
        public const long IsNewExpForAudioApiByDefault = 0x162;  // bool
        public const long ListenerCFrame = 0x108;  // CoordinateFrame
        public const long ListenerObject = 0xd0;
        public const long ListenerType = 0x154;
        public const long OcclusionEnabled = 0x163;  // bool
        public const long RespectFilteringEnabled = 0x164;  // bool
        public const long ReverbEnabled = 0x165;  // bool
        public const long RolloffScale = 0x158;  // float
        public const long VolumetricAudio = 0x15c;
    }
    public static class Soundscape_TremoloSoundEffect
    {
        public const long Depth = 0xe0;  // float
        public const long Duty = 0xe4;  // float
        public const long Frequency = 0xe8;  // float
    }
    public static class Sparkles
    {
        public const long Enabled = 0xb4;  // bool
        public const long LocalTransparencyModifier = 0xac;  // float
        public const long SparkleColor = 0xa0;  // Color3
        public const long TimeScale = 0xb0;  // float
    }
    public static class SpawnLocation
    {
        public const long AllowTeamChangeOnTouch = 0x1c8;  // bool
        public const long Duration = 0x1c0;  // int
        public const long Enabled = 0x1c9;  // bool
        public const long Neutral = 0x1ca;  // bool
        public const long TeamColor = 0x1c4;  // BrickColor
    }
    public static class SpecialShape
    {
        public const long MeshType = 0x120;  // Enums::MeshTypeEnum::MeshType
    }
    public static class SphereHandleAdornment
    {
        public const long DoubleSided = 0x194;  // bool
        public const long Radius = 0x18c;  // float
        public const long Shading = 0x190;  // Enums::AdornShading
    }
    public static class SpotLight
    {
        public const long Angle = 0xbc;  // float
        public const long Face = 0xc0;  // NormalId
        public const long Range = 0xc4;  // float
    }
    public static class StarterGuiService
    {
        public const long ClipsDescendantsSupportsRotation = 0x168;  // Enums::RolloutState
        public const long ProcessUserInput = 0x178;  // bool
        public const long ResetPlayerGuiOnSpawn = 0x179;  // bool
        public const long RtlTextSupport = 0x16c;  // Enums::RtlTextSupport
        public const long ScreenOrientation = 0x170;  // Enums::ScreenOrientationEnum::ScreenOrientation
        public const long ShowDevelopmentGui = 0x17a;  // bool
        public const long VirtualCursorMode = 0x174;  // Enums::VirtualCursorMode
    }
    public static class StarterPlayerService
    {
        public const long AllowCustomAnimations = 0x118;  // bool
        public const long AutoJumpEnabled = 0x119;  // bool
        public const long CameraMaxZoomDistance = 0xc4;  // float
        public const long CameraMinZoomDistance = 0xc8;  // float
        public const long CameraMode = 0xcc;  // Enums::CameraModeEnum::CameraMode
        public const long CharacterBreakJointsOnDeath = 0x11a;  // bool
        public const long CharacterJumpHeight = 0xd0;  // float
        public const long CharacterJumpPower = 0xd4;  // float
        public const long CharacterMaxSlopeAngle = 0xd8;  // float
        public const long CharacterUseJumpPower = 0x11b;  // bool
        public const long CharacterWalkSpeed = 0xdc;  // float
        public const long ClassicDeath = 0x11c;  // bool
        public const long CreateDefaultPlayerModule = 0x11d;  // bool
        public const long DevCameraOcclusionMode = 0xe0;  // Enums::DevCameraOcclusionModeEnum::DeveloperCameraOcclusionMode
        public const long DevComputerCameraMovementMode = 0xe4;  // Enums::DevComputerCameraMovementModeEnum::DeveloperComputerCameraMovementMode
        public const long DevComputerMovementMode = 0xe8;  // Enums::DevComputerMovementModeEnum::DeveloperComputerMovementMode
        public const long DevTouchCameraMovementMode = 0xec;  // Enums::DevTouchCameraMovementModeEnum::DeveloperTouchCameraMovementMode
        public const long DevTouchMovementMode = 0xf0;  // Enums::DevTouchMovementModeEnum::DeveloperTouchMovementMode
        public const long EnableDynamicHeads = 0xf4;  // LoadDynamicHeads
        public const long EnableMouseLockOption = 0x11e;  // bool
        public const long GameSettingsAvatar = 0xf8;  // GameAvatarType
        public const long GameSettingsR15Collision = 0xfc;  // R15CollisionType
        public const long HealthDisplayDistance = 0x100;  // float
        public const long LoadCharacterAppearance = 0x11f;  // bool
        public const long NameDisplayDistance = 0x10c;  // float
        public const long PlayerModuleStatus = 0x110;  // int
        public const long UseImprovedCharacterEvents = 0x114;  // Enums::RolloutState
        public const long UserEmotesEnabled = 0x120;  // bool
    }
    public static class StateMachineDefinition
    {
        public const long NodeId = 0x98;
    }
    public static class StateMachineTransitionDefinition
    {
        public const long Priority = 0xd0;  // int
        public const long TransitionId = 0x98;
    }
    public static class StringValue
    {
        public const long Value = 0xa0;
    }
    public static class StudioData
    {
        public const long EnableScriptCollabByDefaultOnLoad = 0xb0;  // bool
    }
    public static class Styling_StyleDerive
    {
        public const long Index = 0xb0;  // int
        public const long Priority = 0xb4;  // int
    }
    public static class Styling_StyleRule
    {
        public const long Index = 0x140;  // int
        public const long Priority = 0x144;  // int
        public const long Selector = 0x110;
    }
    public static class SunRaysEffect
    {
        public const long Intensity = 0x98;  // float
        public const long Spread = 0x9c;  // float
    }
    public static class SurfaceAppearance
    {
        public const long AlphaMode = 0x1a8;  // TexturePackAlphaMode
        public const long Color = 0x190;  // Color3
        public const long ColorMapContent = 0xa0;  // Content
        public const long EmissiveMaskContent = 0xc8;  // Content
        public const long EmissiveStrength = 0x1ac;  // float
        public const long EmissiveTint = 0x19c;  // Color3
        public const long MetalnessMapContent = 0xf0;  // Content
        public const long NormalMapContent = 0x118;  // Content
        public const long ResampleMode = 0x1b0;  // Enums::ImageResampleMode
        public const long RoughnessMapContent = 0x140;  // Content
        public const long SurfaceSlot = 0x1b4;  // int
    }
    public static class SurfaceGui
    {
        public const long HorizontalCurvature = 0x79c;  // float
        public const long MaxDistance = 0x7a4;  // float
        public const long Shape = 0x7ac;  // SurfaceGuiShape
    }
    public static class SurfaceGuiBase
    {
        public const long Active = 0x6ac;  // bool
        public const long Face = 0x6a8;  // NormalId
    }
    public static class SurfaceLight
    {
        public const long Angle = 0xbc;  // float
        public const long Face = 0xc0;  // NormalId
        public const long Range = 0xc4;  // float
    }
    public static class SurfaceSelection
    {
        public const long TargetSurface = 0xe8;  // NormalId
    }
    public static class SwimController
    {
        public const long AccelerationTime = 0xc0;  // float
        public const long PitchMaxTorque = 0xc4;  // float
        public const long PitchSpeedFactor = 0xc8;  // float
        public const long RollMaxTorque = 0xcc;  // float
        public const long RollSpeedFactor = 0xd0;  // float
    }
    public static class Team
    {
        public const long AutoAssignable = 0xa4;  // bool
        public const long AutoColorCharacters = 0xa5;  // bool
        public const long ChildOrder = 0x98;  // int
        public const long Score = 0x9c;  // int
        public const long TeamColor = 0xa0;  // BrickColor
    }
    public static class TeleportOptions
    {
        public const long ReservedServerAccessCode = 0x98;
        public const long ReservedServerId = 0xb0;
        public const long ServerInstanceId = 0xc8;
        public const long ShouldReserveServer = 0xf8;  // bool
        public const long VipServerId = 0xe0;
    }
    public static class TeleportService
    {
        public const long CustomizedTeleportUI = 0xb0;  // bool
    }
    public static class TerrainDetail
    {
        public const long ColorMapContent = 0xa0;  // Content
        public const long EmissiveMaskContent = 0xc8;  // Content
        public const long EmissiveStrength = 0x19c;  // float
        public const long EmissiveTint = 0x190;  // Color3
        public const long Face = 0x1a0;  // TerrainFace
        public const long MaterialPattern = 0x1a4;  // MaterialPattern
        public const long MetalnessMapContent = 0xf0;  // Content
        public const long NormalMapContent = 0x118;  // Content
        public const long RoughnessMapContent = 0x140;  // Content
        public const long StudsPerTile = 0x1a8;  // float
    }
    public static class TestService
    {
        public const long AutoRuns = 0xe8;  // bool
        public const long Description = 0xa8;
        public const long ExecuteWithStudioRun = 0xe9;  // bool
        public const long Is30FpsThrottleEnabled = 0xec;  // bool
        public const long IsPhysicsEnvironmentalThrottled = 0xea;  // bool
        public const long IsSleepAllowed = 0xeb;  // bool
        public const long NumberOfPlayers = 0xdc;  // int
        public const long SimulateSecondsLag = 0xc8;  // double
        public const long ThrottlePhysicsToRealtime = 0xec;  // bool
        public const long Timeout = 0xd0;  // double
    }
    public static class Text_GetTextBoundsParams
    {
        public const long Font = 0xb8;
        public const long RichText = 0xc8;  // bool
        public const long Size = 0xc0;  // float
        public const long Text = 0xa0;
        public const long Width = 0xc4;  // float
    }
    public static class TextBox
    {
        public const long Confidential = 0xed9;  // bool
        public const long LocalizationMatchIdentifier = 0xdf8;
        public const long LocalizationMatchedSourceText = 0xe10;
        public const long ManualFocusRelease = 0xedb;  // bool
        public const long OverlayNativeInput = 0xedd;  // bool
        public const long PlaceholderColor3 = 0xe80;  // Color3; heuristic decode, passed live check
        public const long ReturnKeyType = 0xeb0;  // Enums::ReturnKeyTypeEnum::ReturnKeyType
        public const long ShouldEmitReturnEvents = 0xedf;  // bool
        public const long ShouldEmitTabEvents = 0xee0;  // bool
        public const long ShouldEmitUpAndDownArrowEvents = 0xee1;  // bool
        public const long TextColor3 = 0xe8c;  // Color3; heuristic decode, passed live check
        public const long TextInputType = 0xebc;  // Enums::TextInputTypeEnum::TextInputType
    }
    public static class TextChannel
    {
        public const long AddPlayersOnJoin = 0xa8;  // bool
        public const long IsDefaultTextChannel = 0xa9;  // bool
    }
    public static class TextChannelWindow
    {
        public const long Target = 0x9a0;
        public const long UseDefaultFont = 0x9b9;  // bool
    }
    public static class TextChatCommand
    {
        public const long AutocompleteVisible = 0xc8;  // bool
        public const long Enabled = 0xc9;  // bool
        public const long PrimaryAlias = 0x98;
        public const long SecondaryAlias = 0xb0;
    }
    public static class TextChatMessage
    {
        public const long BubbleChatMessageProperties = 0x1f0;
        public const long ChatActionType = 0xa0;
        public const long ChatWindowMessageProperties = 0x200;
        public const long ForModeration = 0x244;  // bool
        public const long IsHiddenMessage = 0x245;  // bool
        public const long IsHistorical = 0x246;  // bool
        public const long MessageId = 0xb8;
        public const long Metadata = 0xd0;
        public const long OriginalText = 0xe8;
        public const long PrefixTextInternal = 0x118;
        public const long PresetChatVersion = 0x130;
        public const long PresetId = 0x148;
        public const long RewrittenText = 0x160;
        public const long RewrittenTranslation = 0x178;
        public const long TextChannel = 0x210;
        public const long TextInternal = 0x1a8;
        public const long TextSource = 0x220;
        public const long TranslationInternal = 0x1d8;
        public const long Verified = 0x247;  // bool
        public const long WasRewritten = 0x248;  // bool
    }
    public static class TextChatService
    {
        public const long ChatVersion = 0x1e0;  // Enums::ChatVersion
        public const long CreateDefaultCommands = 0x1eb;  // bool
        public const long CreateDefaultTextChannels = 0x1ec;  // bool
        public const long HasSeenDeprecationDialog = 0x1ed;  // bool
        public const long IsLegacyChatDisabled = 0x1ee;  // bool
        public const long PlatformIntegratedChat = 0x1e4;  // Enums::RolloutState
    }
    public static class TextGenerator
    {
        public const long Seed = 0xb0;  // int
        public const long SystemPrompt = 0x98;
        public const long Temperature = 0xb4;  // float
        public const long TopP = 0xb8;  // float
    }
    public static class TextLabel
    {
        public const long Confidential = 0xea4;  // bool
        public const long LocalizationMatchIdentifier = 0xdf8;
        public const long LocalizationMatchedSourceText = 0xe10;
        public const long TextColor3 = 0xe68;  // Color3; heuristic decode, passed live check
        public const long TextStrokeColor3 = 0xe74;  // Color3; heuristic decode, passed live check
    }
    public static class TextSource
    {
        public const long CanSend = 0xd0;  // bool
        public const long DisplayName = 0x98;
        public const long Username = 0xb0;
    }
    public static class Tool
    {
        public const long CanBeDropped = 0x430;  // bool
        public const long Enabled = 0x431;  // bool
        public const long Grip = 0x400;  // CoordinateFrame
        public const long GripForward = 0x408;  // Vector3
        public const long GripPos = 0x424;  // Vector3
        public const long GripRight = 0x400;  // Vector3
        public const long GripUp = 0x404;  // Vector3
        public const long ManualActivationOnly = 0x432;  // bool
        public const long RequiresHandle = 0x433;  // bool
        public const long ToolTip = 0x3e8;
    }
    public static class Trail
    {
        public const long Brightness = 0x1a0;  // float
        public const long Color = 0x120;  // ColorSequence
        public const long Enabled = 0x1c4;  // bool
        public const long FaceCamera = 0x1c5;  // bool
        public const long Lifetime = 0x1a4;  // float
        public const long LightEmission = 0x1a8;  // float
        public const long LightInfluence = 0x1ac;  // float
        public const long LocalTransparencyModifier = 0x1b0;  // float
        public const long MaxLength = 0x1b4;  // float
        public const long MinLength = 0x1b8;  // float
        public const long TextureLength = 0x1bc;  // float
        public const long TextureMode = 0x1c0;  // TextureMode
        public const long Transparency = 0xa0;  // NumberSequence
        public const long WidthScale = 0xe0;  // NumberSequence
    }
    public static class TriangleMeshPart
    {
        public const long InertiaMigrated = 0x238;  // bool
        public const long PCDRequestId = 0x230;  // int
    }
    public static class UIAspectRatioConstraint
    {
        public const long AspectRatio = 0xa8;  // float; heuristic decode, passed live check
    }
    public static class UIDragDetector
    {
        public const long BoundingBehavior = 0x178;  // UIDragDetectorBoundingBehavior
        public const long BoundingUI = 0xf8;
        public const long DragAxis = 0x170;  // Vector2
        public const long DragRelativity = 0x17c;  // UIDragDetectorDragRelativity
        public const long DragRotation = 0x180;  // float
        public const long DragSpace = 0x184;  // UIDragDetectorDragSpace
        public const long DragStyle = 0x188;  // UIDragDetectorDragStyle
        public const long DragUDim2 = 0x130;  // UDim2
        public const long Enabled = 0x1a0;  // bool
        public const long MaxDragAngle = 0x18c;  // float
        public const long MaxDragTranslation = 0x140;  // UDim2
        public const long MinDragAngle = 0x190;  // float
        public const long MinDragTranslation = 0x150;  // UDim2
        public const long ReferenceUIInstance = 0x108;
        public const long ResponseStyle = 0x194;  // UIDragDetectorResponseStyle
        public const long Selectable = 0x1a1;  // bool
        public const long SelectionModeDragSpeed = 0x160;  // UDim2
        public const long SelectionModeRotateSpeed = 0x198;  // float
        public const long UIDragSpeedAxisMapping = 0x19c;  // Enums::UIDragSpeedAxisMapping
    }
    public static class UIGradient
    {
        public const long Rotation = 0x120;  // float; heuristic decode, passed live check
        public const long Scale = 0x124;  // float; heuristic decode, passed live check
    }
    public static class UIPageLayout
    {
        public const long Animated = 0x154;  // bool
        public const long Circular = 0x155;  // bool
        public const long EasingDirection = 0x148;  // Enums::EasingDirection
        public const long EasingStyle = 0x14c;  // Enums::EasingStyle
        public const long GamepadInputEnabled = 0x156;  // bool
        public const long Padding = 0x140;  // UDim
        public const long ScrollWheelInputEnabled = 0x157;  // bool
        public const long TouchInputEnabled = 0x158;  // bool
        public const long TweenTime = 0x150;  // float
    }
    public static class UISizeConstraint
    {
        public const long MaxSize = 0xa8;  // Vector2; heuristic decode, passed live check
        public const long MinSize = 0xb0;  // Vector2; heuristic decode, passed live check
    }
    public static class UIStroke
    {
        public const long Color = 0xa8;  // Color3; heuristic decode, passed live check
        public const long Thickness = 0xcc;  // float; heuristic decode, passed live check
    }
    public static class UITableLayout
    {
        public const long FillEmptySpaceColumns = 0x14c;  // bool
        public const long FillEmptySpaceRows = 0x14d;  // bool
        public const long MajorAxis = 0x148;  // Enums::TableMajorAxisEnum::TableMajorAxis
        public const long Padding = 0x138;  // UDim2
    }
    public static class UserInputService
    {
        public const long LegacyInputEventsEnabled = 0xd8;  // bool
    }
    public static class VRService
    {
        public const long AutomaticScaling = 0xf8;  // Enums::VRScaling
        public const long AvatarGestures = 0x114;  // bool
        public const long ControllerModels = 0xfc;  // Enums::VRControllerModelMode
        public const long FadeOutViewOnCollision = 0x116;  // bool
        public const long GuiInputUserCFrame = 0x100;  // Enums::UserCFrameEnum::UserCFrame
        public const long LaserPointer = 0x104;  // Enums::VRLaserPointerMode
        public const long QuestASWState = 0x117;  // bool
        public const long QuestDisplayRefreshRate = 0x10c;  // float
    }
    public static class Vector3Value
    {
        public const long Value = 0xa0;  // Vector3
    }
    public static class VehicleSeat
    {
        public const long HeadsUpDisplay = 0x215;  // bool
        public const long MaxSpeed = 0x200;  // float
        public const long Steer = 0x204;  // int
        public const long SteerFloat = 0x204;  // float
        public const long Throttle = 0x208;  // int
        public const long ThrottleFloat = 0x208;  // float
        public const long Torque = 0x20c;  // float
        public const long TurnSpeed = 0x210;  // float
    }
    public static class VelocityMotor
    {
        public const long CurrentAngle = 0xe0;  // float; at *(object + 0x168) + this
        public const long DesiredAngle = 0xf8;  // float; at *(object + 0x168) + this
        public const long Hole = 0x178;
        public const long MaxVelocity = 0xf4;  // float; at *(object + 0x168) + this
    }
    public static class VersionControlService
    {
        public const long ScriptCollabEnabled = 0x100;  // bool
        public const long ScriptCollabVersionHistoryEnabled = 0x101;  // bool
    }
    public static class VideoCaptureService
    {
        public const long CameraID = 0xb0;
    }
    public static class VideoDisplay
    {
        public const long ScaleType = 0xa80;  // Enums::ImageScale
        public const long TileSize = 0xa50;  // UDim2
        public const long VideoColor3 = 0xa60;  // Color3
        public const long VideoRectOffset = 0xa6c;  // Vector2
        public const long VideoRectSize = 0xa74;  // Vector2
        public const long VideoTransparency = 0xa84;  // float
    }
    public static class VideoFrame
    {
        public const long InternalVideoUsage = 0x9d8;  // VideoUsage
        public const long Looped = 0x9f0;  // bool
        public const long MaximumResolution = 0x9dc;  // VideoSampleSize
        public const long Playing = 0x9f1;  // bool
        public const long PlayingReplicating = 0x9f1;  // bool
        public const long RollOffMaxDistance = 0x9e0;  // float
        public const long RollOffMinDistance = 0x9e4;  // float
        public const long RollOffMode = 0x9e8;  // Soundscape::RollOffMode
        public const long TimePosition = 0x9d0;  // double
        public const long TimePositionReplicating = 0x9d0;  // double
        public const long VideoContent = 0x9a8;  // Content
        public const long Volume = 0x9ec;  // float
    }
    public static class VideoPlayer
    {
        public const long AutoLoadInStudio = 0x161;  // bool
        public const long AutoPlayInStudio = 0x162;  // bool
        public const long InternalVideoUsage = 0x150;  // VideoUsage
        public const long Looping = 0x164;  // bool
        public const long MaximumResolution = 0x154;  // VideoSampleSize
        public const long PlaybackSpeed = 0x158;  // float
        public const long PlayingReplicating = 0x160;  // bool
        public const long VideoContent = 0x120;  // Content
        public const long Volume = 0x15c;  // float
    }
    public static class ViewportFrame
    {
        public const long CameraCFrame = 0x9b8;  // CoordinateFrame
        public const long CameraFieldOfView = 0xa18;  // float
        public const long IsMirrored = 0xa20;  // bool
    }
    public static class VirtualInputManager
    {
        public const long AdditionalLuaState = 0x120;
    }
    public static class VisualizationMode
    {
        public const long Enabled = 0xc8;  // bool
        public const long Title = 0x98;
        public const long ToolTip = 0xb0;
    }
    public static class VisualizationModeCategory
    {
        public const long Enabled = 0xb0;  // bool
        public const long Title = 0x98;
    }
    public static class VoiceChatService
    {
        public const long DefaultDistanceAttenuation = 0x1e0;  // Enums::VoiceChatDistanceAttenuationType
        public const long EnableDefaultVoice = 0x1ec;  // bool
        public const long EnableVoiceVolumeControls = 0x1e4;  // Enums::RolloutState
        public const long UseAudioApi = 0x1e8;  // Enums::AudioApiRollout
        public const long UseNewAudioApi = 0x1ed;  // bool
        public const long UseNewControlPaths = 0x1ee;  // bool
        public const long UseNewJoinFlow = 0x1ef;  // bool
        public const long UseStreamSwitching = 0x1f0;  // bool
        public const long VoiceChatEnabledForPlaceOnRcc = 0x1f1;  // bool
        public const long VoiceChatEnabledForUniverseOnRcc = 0x1f2;  // bool
    }
    public static class Weld
    {
        public const long EnableSkinning = 0x170;  // bool
    }
    public static class Wire
    {
        public const long SourceName = 0xa0;
        public const long TargetName = 0xb8;
    }
    public static class WireframeHandleAdornment
    {
        public const long Scale = 0x18c;  // Vector3
        public const long Thickness = 0x198;  // float
    }
    public static class WorldModel
    {
        public const long UseWorkspaceCollisionGroups = 0x428;  // bool
    }
    public static class WorldRoot
    {
        public const long AutoSimulate = 0x324;  // bool
        public const long GravityDirection = 0x300;  // Vector3
        public const long SimulationRate = 0x31c;  // float
        public const long Wind = 0x320;  // float
        public const long WindDirection = 0x30c;  // Vector3
    }
    public static class WrapLayer
    {
        public const long AutoSkin = 0x3a4;  // WrapLayerAutoSkin
        public const long BindOffset = 0x320;  // CoordinateFrame
        public const long Color = 0x380;  // Color3
        public const long DebugMode = 0x3a8;  // WrapLayerDebugMode
        public const long Enabled = 0x3bc;  // bool
        public const long MaxSize = 0x38c;  // Vector3
        public const long Offset = 0x398;  // Vector3
        public const long Order = 0x3ac;  // int
        public const long Puffiness = 0x3b0;  // float
        public const long ReferenceMeshContent = 0x280;  // Content
        public const long ReferenceOrigin = 0x350;  // CoordinateFrame
        public const long RotateScaleDeformationMap = 0x2a8;  // Content
        public const long ScaleOnlyDeformationMap = 0x2d0;  // Content
        public const long ShrinkFactor = 0x3b4;  // float
        public const long TargetShaping = 0x3b8;  // float
    }
    public static class WrapTarget
    {
        public const long Color = 0x280;  // Color3
        public const long DebugMode = 0x28c;  // WrapTargetDebugMode
        public const long Stiffness = 0x290;  // float
    }
    public static class WrapTextureTransfer
    {
        public const long UVMaxBound = 0xc0;  // Vector2
        public const long UVMinBound = 0xc8;  // Vector2
    }
}
