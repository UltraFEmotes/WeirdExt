// WeirdExt offsets — macOS ARM64
//
// Roblox Version  : 0.745.0.7451137
// Binary SHA-256  : 8af3f95d347a5283618dd9c17f4a1b02b59982ff699f00cc6f2a195377f2f6b7
// Dumped At       : 2026-11-14 20:54 UTC
// Total Offsets   : 29
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
    }
    public static class Players
    {
        public const long LocalPlayer = 0x108;
    }
    public static class Player
    {
        public const long ModelInstance = 0x258;
        public const long Team = 0x298;
    }
    public static class Workspace
    {
        public const long CurrentCamera = 0x458;
    }
    public static class Camera
    {
        public const long Rotation = 0xb8;  // nine floats, row-major; Position follows at +36
        public const long Position = 0xdc;
        public const long FieldOfView = 0x120;  // float, radians (vertical)
        public const long CameraSubject = 0xa8;  // (object, control block) smart pointer pair
    }
    public static class BasePart
    {
        public const long Primitive = 0x168;
    }
    public static class Primitive
    {
        public const long Rotation = 0xb0;  // nine floats, row-major; Position follows at +36
        public const long Position = 0xd4;
        public const long Flags = 0x1be;
        public const long AssemblyLinearVelocity = 0xe0;  // copy refreshed from the solver body each physics step
    }
    public static class Humanoid
    {
        public const long Health = 0x174;
        public const long MaxHealth = 0x18c;
        public const long WalkSpeed = 0x1b4;
        public const long WalkSpeedCheck = 0x38c;  // must equal WalkSpeed
        public const long JumpPower = 0x188;
        public const long UseJumpPower = 0x1c6;  // bool
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
}
