using UnrealBuildTool;

public class FPSGazeCore : ModuleRules
{
    public FPSGazeCore(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Projects"
        });

        PublicDefinitions.Add("WITH_TOBII_EYETRACKING=0");
    }
}
