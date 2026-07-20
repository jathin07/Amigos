export const destinationThemes = {
  munnar: {
    mood: "Misty Escape",
    tagline: "Wake up above the clouds",
    personality: "Romantic, peaceful, and close to nature.",
    accent: "emerald", // Used dynamically to generate classes
    effect: "mist",
    heroImage: "/images/places/munnar.jpg",
    quote: "In the gardens of Munnar, every leaf tells a green story.",
    weatherRules: {
      Clear: {
        tip: "Ideal day to trek Anamudi peak or visit top station for clear valley views.",
        packing: "Sunscreen, polarized sunglasses, light layer",
        activity: "Hill summit trekking & scenic photography"
      },
      Clouds: {
        tip: "Tea plantations look magical in the cloud cover. Perfect lighting for portraits.",
        packing: "Light sweater or windcheater, walking shoes",
        activity: "Tea museum tour & garden walk"
      },
      Rain: {
        tip: "Waterfalls like Attukad and Lakkam are roaring. Keep electronics in dry bags.",
        packing: "High-quality raincoat, sturdy umbrella, extra socks",
        activity: "Waterfall spotting & hot tea sipping"
      },
      Default: {
        tip: "Enjoy the pristine tea hills and breathe in the fresh mountain air.",
        packing: "Light jacket, walking shoes",
        activity: "Spice garden tour & local sightseeing"
      }
    }
  },
  coorg: {
    mood: "Coffee Trails",
    tagline: "Breathe in the aroma of the hills",
    personality: "Cozy, misty, and rich with coffee plantations.",
    accent: "green",
    effect: "rain",
    heroImage: "/images/places/coorg.jpg",
    quote: "Where the coffee aroma lingers and the valleys whisper peace.",
    weatherRules: {
      Clear: {
        tip: "Clear skies are perfect for trekking Mandalpatti or visiting Abbey Falls.",
        packing: "Hat, sunglasses, trekking boots",
        activity: "Mandalpatti 4x4 Jeep safari"
      },
      Clouds: {
        tip: "A misty day is perfect to visit the Golden Temple (Namdroling Monastery).",
        packing: "Light shawl or cardigan, cameras",
        activity: "Tibetan Monastery exploration"
      },
      Rain: {
        tip: "Heavy rains make the rivers wild. Great for rafting if safety permits.",
        packing: "Raincoat, quick-dry clothes, waterproof shoes",
        activity: "River rafting or cozy indoor homestay vibes"
      },
      Default: {
        tip: "Walk through coffee estates and discover the heritage of Coorg.",
        packing: "Walking shoes, umbrella",
        activity: "Coffee plantation guided walk"
      }
    }
  },
  pondicherry: {
    mood: "Coastal Charm",
    tagline: "French streets and ocean breeze",
    personality: "Colonial heritage, beachside tranquility, and spiritual aura.",
    accent: "cyan",
    effect: "waves",
    heroImage: "/images/places/pondicherry.jpg",
    quote: "A quiet corner where French elegance meets the Indian Ocean.",
    weatherRules: {
      Clear: {
        tip: "Great day for surfing at Serenity Beach or walking along Promenade Beach.",
        packing: "Sunscreen, breathable cotton wear, beach slippers",
        activity: "Surfing lessons or cycling in White Town"
      },
      Clouds: {
        tip: "Perfect weather for cafe hopping and admiring the colonial architecture.",
        packing: "Comfortable sandals, camera",
        activity: "French Quarter architectural walk"
      },
      Rain: {
        tip: "Enjoy the sound of rain on French balconies. Visit Auroville's indoor sections.",
        packing: "Umbrella, light sandals",
        activity: "Bistro dining & spiritual reading"
      },
      Default: {
        tip: "Relax by the shore and catch a beautiful sunrise over the bay.",
        packing: "Sunglasses, cotton clothes",
        activity: "Promenade walk & French cuisine tasting"
      }
    }
  },
  gokarna: {
    mood: "Coastal Trekking",
    tagline: "Where the cliffs meet the ocean",
    personality: "Adventurous, beachy, and laid-back.",
    accent: "indigo",
    effect: "waves",
    heroImage: "/images/places/gokarna.jpg",
    quote: "Trek over rocky cliffs and wake up to the rhythm of beach waves.",
    weatherRules: {
      Clear: {
        tip: "Perfect conditions for the famous 5-Beach Cliff Trek. Start early in the morning.",
        packing: "Trek shoes, reusable water bottle, sunscreen",
        activity: "5-Beach Cliff Trekking (Kudle to Paradise)"
      },
      Clouds: {
        tip: "Cooler temperature makes trekking less tiring. Sunset from cliffs will be dreamy.",
        packing: "Trek pants, torch (for night return)",
        activity: "Sunset cliff watching & beach volleyball"
      },
      Rain: {
        tip: "Sea is rough. Trekking path can be slippery. Stay safe inside beach shacks.",
        packing: "Waterproof dry bag, non-slip footwear",
        activity: "Shack music sessions & sea watching"
      },
      Default: {
        tip: "Dip your toes in the beach sand and try fresh local sea delicacies.",
        packing: "Beachwear, slippers",
        activity: "Temple visit & beach cafe hopping"
      }
    }
  },
  ooty: {
    mood: "Nilgiri Magic",
    tagline: "Queen of hill stations",
    personality: "Cool breezes, botanical gardens, and scenic train rides.",
    accent: "teal",
    effect: "mist",
    heroImage: "/images/places/ooty.jpg",
    quote: "Misty pine forests and the nostalgic whistle of the toy train.",
    weatherRules: {
      Clear: {
        tip: "Perfect day to ride the Nilgiri Mountain Railway toy train or boat in Ooty Lake.",
        packing: "Cap, sunglasses, light sweater",
        activity: "Toy train ride & botanical gardens stroll"
      },
      Clouds: {
        tip: "Visit Doddabetta Peak; clouds drifting across the telescope house look amazing.",
        packing: "Warm jacket, comfortable shoes",
        activity: "Doddabetta Peak viewpoints exploration"
      },
      Rain: {
        tip: "Temperature drops quickly in rain. Warm up with fresh local hot chocolate.",
        packing: "Thermal innerwear, rain jacket, umbrella",
        activity: "Chocolate tasting & tea tasting factory visit"
      },
      Default: {
        tip: "Explore the vast green tea estates of the Nilgiris.",
        packing: "Light woolens, walking shoes",
        activity: "Pykara waterfalls & lake sightseeing"
      }
    }
  },
  wayanad: {
    mood: "Forest Wonders",
    tagline: "Explore the green heart of Kerala",
    personality: "Wild, dense green, and filled with waterfalls.",
    accent: "lime",
    effect: "leaves",
    heroImage: "/images/places/wayanad.jpg",
    quote: "Lose yourself in the bamboo trails and ancient cave histories.",
    weatherRules: {
      Clear: {
        tip: "Climb Chembra Peak for a view of the heart-shaped lake. Clear weather is mandatory.",
        packing: "Trekking permit cash, trekking shoes, sun hat",
        activity: "Chembra Peak heart-lake trek"
      },
      Clouds: {
        tip: "Explore the Edakkal Caves. The rock-cut carvings have great ambient light today.",
        packing: "Comfortable shoes with grip, camera",
        activity: "Edakkal Caves historic hike"
      },
      Rain: {
        tip: "Monsoon cascades at Banasura Sagar Dam and Soochipara Falls are in full glory.",
        packing: "Waterproof poncho, leech socks for trekking",
        activity: "Banasura Sagar Dam reservoir view"
      },
      Default: {
        tip: "Drive through the green forest ghat roads and spot local wildlife.",
        packing: "Binoculars, insect repellent",
        activity: "Muthanga wildlife sanctuary safari"
      }
    }
  },
  default: {
    mood: "Adventure Call",
    tagline: "Map your next big adventure",
    personality: "Scenic roads, warm locals, and memorable sights.",
    accent: "blue",
    effect: "mist",
    heroImage: "/images/places/munnar.jpg",
    quote: "Collect memories, leave only footprints behind.",
    weatherRules: {
      Clear: {
        tip: "Clear skies mean great conditions for all outdoor adventures and drives.",
        packing: "Sun protection, comfortable shoes",
        activity: "Sightseeing & local exploration"
      },
      Clouds: {
        tip: "Perfect weather for long walks and outdoor cafe dining.",
        packing: "Light layer, camera",
        activity: "Cultural tour & local markets"
      },
      Rain: {
        tip: "Waterfalls and rivers will be active. Keep rain gear handy.",
        packing: "Umbrella, water-resistant layers",
        activity: "Museum visits & local cafe hopping"
      },
      Default: {
        tip: "Enjoy your trip and stay safe on roads.",
        packing: "Comfortable clothing, walking shoes",
        activity: "Local sightseeing & dining"
      }
    }
  }
};

// Helper utility to safely fetch theme details
export const getDestinationTheme = (name) => {
  if (!name) return destinationThemes.default;
  const key = name.toLowerCase().trim();
  return destinationThemes[key] || destinationThemes.default;
};

// Helper utility to retrieve class styles based on accent color names
export const getAccentClasses = (accent) => {
  const styles = {
    emerald: {
      text: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-emerald-100",
      hoverBorder: "hover:border-emerald-300",
      ring: "ring-emerald-500",
      badge: "bg-emerald-100 text-emerald-800",
      gradient: "from-emerald-400 to-teal-500",
      textHover: "group-hover:text-emerald-600",
      glow: "shadow-emerald-500/10 hover:shadow-emerald-500/20"
    },
    green: {
      text: "text-green-600",
      bg: "bg-green-50",
      border: "border-green-100",
      hoverBorder: "hover:border-green-300",
      ring: "ring-green-500",
      badge: "bg-green-100 text-green-800",
      gradient: "from-green-400 to-emerald-500",
      textHover: "group-hover:text-green-600",
      glow: "shadow-green-500/10 hover:shadow-green-500/20"
    },
    cyan: {
      text: "text-cyan-600",
      bg: "bg-cyan-50",
      border: "border-cyan-100",
      hoverBorder: "hover:border-cyan-300",
      ring: "ring-cyan-500",
      badge: "bg-cyan-100 text-cyan-800",
      gradient: "from-cyan-400 to-blue-500",
      textHover: "group-hover:text-cyan-600",
      glow: "shadow-cyan-500/10 hover:shadow-cyan-500/20"
    },
    indigo: {
      text: "text-indigo-600",
      bg: "bg-indigo-50",
      border: "border-indigo-100",
      hoverBorder: "hover:border-indigo-300",
      ring: "ring-indigo-500",
      badge: "bg-indigo-100 text-indigo-800",
      gradient: "from-indigo-400 to-purple-500",
      textHover: "group-hover:text-indigo-600",
      glow: "shadow-indigo-500/10 hover:shadow-indigo-500/20"
    },
    teal: {
      text: "text-teal-600",
      bg: "bg-teal-50",
      border: "border-teal-100",
      hoverBorder: "hover:border-teal-300",
      ring: "ring-teal-500",
      badge: "bg-teal-100 text-teal-800",
      gradient: "from-teal-400 to-cyan-500",
      textHover: "group-hover:text-teal-600",
      glow: "shadow-teal-500/10 hover:shadow-teal-500/20"
    },
    lime: {
      text: "text-lime-700",
      bg: "bg-lime-50",
      border: "border-lime-100",
      hoverBorder: "hover:border-lime-300",
      ring: "ring-lime-500",
      badge: "bg-lime-100 text-lime-800",
      gradient: "from-lime-400 to-green-500",
      textHover: "group-hover:text-lime-700",
      glow: "shadow-lime-500/10 hover:shadow-lime-500/20"
    },
    blue: {
      text: "text-blue-600",
      bg: "bg-blue-50",
      border: "border-blue-100",
      hoverBorder: "hover:border-blue-300",
      ring: "ring-blue-500",
      badge: "bg-blue-100 text-blue-800",
      gradient: "from-blue-400 to-cyan-500",
      textHover: "group-hover:text-blue-600",
      glow: "shadow-blue-500/10 hover:shadow-blue-500/20"
    }
  };
  return styles[accent] || styles.blue;
};
