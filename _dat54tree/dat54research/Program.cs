using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;

namespace dat54research
{
    public struct SoundSetNode
    {
        public string Dat54File;
        public string SoundSetName;
        public string SoundSetScriptName;
        public string SoundSetSoundName;
    }

    class Dat54Evaluator
    {
        public void Run()
        {
            DateTime start = DateTime.Now;

            List<SoundSetNode> soundSetsToEvaluate = new List<SoundSetNode>();
            Dictionary<string, XmlDocument> xmlCache = new Dictionary<string, XmlDocument>();

            foreach (var xml in LoadXmls())
            {
                FileInfo xmlFile = xml.Item1;
                XmlDocument xmlDoc = xml.Item2;

                xmlCache.Add(xmlFile.Name, xmlDoc);

                XmlNode itemsNode = xmlDoc.GetElementsByTagName("Items")[0];

                if (itemsNode == null)
                {
                    continue;
                }

                foreach (XmlNode itemNode in itemsNode)
                {
                    XmlAttribute attrib = itemNode.Attributes["type"];

                    if (attrib.Value == "SoundSet")
                    {
                        List<SoundSetNode> nodes = EvaluateSoundSet(xmlFile, itemNode);

                        if (nodes != null)
                        {
                            soundSetsToEvaluate.AddRange(nodes);
                        }
                    }
                }
            }

            int i = 0;
            int n = 0;
            List<string> chains = new List<string>();

            foreach (SoundSetNode soundSetNode in soundSetsToEvaluate)
            {
                n++;
                bool found = xmlCache.TryGetValue(soundSetNode.Dat54File, out XmlDocument xmlDoc);

                if (!found)
                {
                    Console.WriteLine($"{soundSetNode.Dat54File} was not cached.");
                    continue;
                }

                string result = ResolveChain(xmlDoc, soundSetNode);

                if (!string.IsNullOrEmpty(result))
                {
                    chains.Add(result);

                    string time = (DateTime.Now - start).ToString("mm\\:ss");
                    Console.WriteLine(time + " - Evaluated chains " + n + " out of " + soundSetsToEvaluate.Count + " (" + Math.Round((((float)n/(float)soundSetsToEvaluate.Count)*100), 3) + $"%) [{soundSetNode.Dat54File}]");
                }

                if (chains.Count > 1000)
                {
                    string outDir = Path.Join(AppDomain.CurrentDomain.BaseDirectory, "out");

                    if (!Directory.Exists(outDir))
                    {
                        Directory.CreateDirectory(outDir);
                    }

                    string outFile = Path.Join(outDir, $"chains{++i}.txt");
                    string stringyBoi = "";

                    foreach (string c in chains)
                    {
                        stringyBoi += c;
                    }

                    File.WriteAllText(outFile, stringyBoi);
                    chains.Clear();
                }
            }

            Console.WriteLine($"Evaluated {soundSetsToEvaluate.Count} nodes");
        }

        public IEnumerable<Tuple<FileInfo, XmlDocument>> LoadXmls(string fileName = "*")
        {
            string rootDir = Path.Join(AppDomain.CurrentDomain.BaseDirectory, "xml");
            DirectoryInfo directoryInfo = new DirectoryInfo(Path.GetFullPath(rootDir));

            foreach (FileInfo fileInfo in directoryInfo.GetFiles())
            {
                if (fileInfo.Extension.Contains("xml") && (fileName == "*" || fileInfo.Name.Contains(fileName)))
                {
                    using StreamReader fileStream = File.OpenText(fileInfo.FullName);
                    XmlDocument doc = new XmlDocument();
                    doc.Load(fileStream);
                    yield return Tuple.Create(fileInfo, doc);
                }
            }
        }

        private List<SoundSetNode> EvaluateSoundSet(FileInfo xmlFile, XmlNode soundSetNode)
        {
            List<SoundSetNode> soundSetEntries = new List<SoundSetNode>();

            string soundSetItem = soundSetNode.FirstChild.InnerText;

            if (!soundSetNode.HasChildNodes) return null;

            XmlNode items = soundSetNode.SelectSingleNode("Items");
            XmlNodeList itemsInItemList = items.SelectNodes("Item");

            foreach (XmlNode itemEntry in itemsInItemList)
            {
                string scriptName = itemEntry.SelectSingleNode("ScriptName").InnerText;
                string soundName = itemEntry.SelectSingleNode("SoundName").InnerText;

                if (soundName == "null_sound")
                {
                    continue;
                }

                SoundSetNode ssn = new SoundSetNode
                {
                    Dat54File = xmlFile.Name,
                    SoundSetName = soundSetItem,
                    SoundSetScriptName = scriptName,
                    SoundSetSoundName = soundName
                };

                soundSetEntries.Add(ssn);
            }

            return soundSetEntries;
        }

        private List<string> alreadyResolvedChains = new List<string>();

        private string ResolveChain(XmlDocument document, SoundSetNode node)
        {
            if (alreadyResolvedChains.Contains(node.SoundSetSoundName))
            {
                return string.Empty;
            }

            StringBuilder chainBuilder = new StringBuilder();
            chainBuilder.AppendLine("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||");
            chainBuilder.AppendLine($"[{node.Dat54File}]");
            chainBuilder.AppendLine($"SoundSet({node.SoundSetSoundName})");

            Stack<string> hashStack = new Stack<string>();
            hashStack.Push(node.SoundSetSoundName);

            string[] eligbleNodes = new string[] {
                "SimpleSound",
                "MultitrackSound",
                "StreamingSound",
                "WrapperSound",
                "LoopingSound",
                "EnvelopeSound",
                "CollapsingStereoSound",
                "VariableBlockSound",
                "RandomizedSound",
                "ModularSynthSound",
                "TwinLoopSound",
                "IfSound",
                "MathOperationSound",
                "SwitchSound",
                "EnvironmentSound",
                "GranularSound",
                "RetriggeredOverlappedSound",
                "ParameterTransformSound",
                "CrossfadeSound",
                "DynamicEntitySound",
                "OnStopSound",
                "KineticSound",
                "FluctuatorSound",
                "SequentialOverlapSound",
                "SequentialSound",
                "AutomationSound",
                "VariablePrintValueSound",
                "SpeechSound",
                "VariableCurveSound",
                "DirectionalSound",
                "ExternalStreamSound",
                "SoundList" //Not sure if we need to parse this.
            };

            //0 = Next value is in Items array in the "key=" attribute.
            //1 = Next value is in AudioTracksNode.
            //2 = Next value is in AudioHash0/1/2/3 (and AudioHash)
            //3 = Next value lives in UnkData -> AudioTrack
            //999 = Terminal node.
            Dictionary<string, int> strategyMap = new Dictionary<string, int>
            {
                { "SimpleSound", 999 },
                { "RandomizedSound", 0 }, 
                { "WrapperSound", 1 },
                { "OnStopSound" , 2 },
                { "MultitrackSound", 1 },
                { "VariableBlockSound", 2 },
                { "EnvelopeSound", 2 },
                { "ModularSynthSound", 999 },
                { "ParameterTransformSound", 2 },
                { "RetriggeredOverlappedSound", 2 },
                { "SwitchSound", 1 },
                { "CollapsingStereoSound", 2 },
                { "SequentialOverlapSound", 1 },
                { "MathOperationSound", 2 },
                { "IfSound", 2 },
                { "LoopingSound", 2 },
                { "TwinLoopSound", 1 },
                { "FluctuatorSound", 2 },
                { "StreamingSound", 1 },
                { "SequentialSound", 1 },
                { "CrossfadeSound", 2 },
                { "VariablePrintValueSound", 999 },
                { "AutomationSound", 2 },
                { "Unknown", 3 },
                { "DynamicEntitySound", 999 },

            };

            XmlNode itemsNode = document.GetElementsByTagName("Items")[0];

            int depth = 0;
            while (hashStack.Count > 0)
            {
                string hash = hashStack.Pop();

                if (hash == "depthdec")
                {
                    depth--;
                    continue;
                }

                foreach (XmlNode itemNode in itemsNode)
                {
                    XmlAttribute attrib = itemNode.Attributes["type"];

                    if (!eligbleNodes.Any(x => x == attrib.Value) && attrib.Value != "SoundSet" && !attrib.Value.Contains("Unknown"))
                    {
                        continue;
                    }

                    XmlNode nameNode = itemNode.SelectSingleNode("Name");
                    if (nameNode.InnerText == hash)
                    {
                        string padding = new string('-', depth + 1);
                        chainBuilder.AppendLine(padding + $" {attrib.Value}({nameNode.InnerText})");

                        bool stratFound = strategyMap.TryGetValue(attrib.Value, out int strat);

                        if (!stratFound)
                        {
                            Console.WriteLine(attrib.Value + " not handled.");
                            continue;
                        }

                        if (strat == 0)
                        {
                            XmlNode audioItemsNode = itemNode.SelectSingleNode("Items");

                            if (audioItemsNode != null && audioItemsNode.HasChildNodes)
                            {
                                hashStack.Push("depthdec");

                                foreach (XmlNode audioTrackChild in audioItemsNode)
                                {
                                    string newHash = audioTrackChild.Attributes["key"].Value;

                                    if (!string.IsNullOrEmpty(newHash))
                                    {
                                        hashStack.Push(newHash);
                                    }
                                }

                                depth++;
                            }
                        }
                        else if (strat == 1)
                        {
                            XmlNode audioTracksNode = itemNode.SelectSingleNode("AudioTracks");

                            if (audioTracksNode != null && audioTracksNode.HasChildNodes)
                            {
                                hashStack.Push("depthdec");

                                foreach (XmlNode audioTrackChild in audioTracksNode)
                                {
                                    string newHash = audioTrackChild.InnerText;

                                    if (!string.IsNullOrEmpty(newHash))
                                    {
                                        hashStack.Push(newHash);
                                    }
                                }

                                depth++;
                            }
                        }
                        else if (strat == 2)
                        {
                            XmlNode[] audioHashNodes = new XmlNode[]
                            {
                                itemNode.SelectSingleNode("AudioHash"),
                                itemNode.SelectSingleNode("AudioHash0"),
                                itemNode.SelectSingleNode("AudioHash1"),
                                itemNode.SelectSingleNode("AudioHash2"),
                                itemNode.SelectSingleNode("AudioHash3"),
                            };

                            hashStack.Push("depthdec");

                            foreach (XmlNode audioHashNode in audioHashNodes)
                            {
                                if (audioHashNode != null)
                                {
                                    string newHash = audioHashNode.InnerText;
                                    if (!string.IsNullOrEmpty(newHash))
                                    {
                                        hashStack.Push(newHash);
                                    }
                                }
                            }

                            depth++;
                        }
                        else if (strat == 3)
                        {
                            XmlNode unkDataNode = itemNode.SelectSingleNode("UnkData");

                            if (unkDataNode != null && unkDataNode.HasChildNodes)
                            {
                                XmlNode unkDataItemNode = unkDataNode.SelectSingleNode("Item");

                                if (unkDataItemNode != null)
                                {
                                    XmlNode audioTrackNode = unkDataItemNode.SelectSingleNode("AudioTrack");

                                    if (audioTrackNode != null && !string.IsNullOrEmpty(audioTrackNode.InnerText))
                                    {
                                        hashStack.Push("depthdec");
                                        hashStack.Push(audioTrackNode.InnerText);
                                    }
                                }

                                depth++;
                            }
                        }
                    }   
                }
            }

            alreadyResolvedChains.Add(node.SoundSetSoundName);
            return chainBuilder.ToString();
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Dat54Evaluator eval = new Dat54Evaluator();
            eval.Run();
            Console.ReadLine();
        }
    }
}
