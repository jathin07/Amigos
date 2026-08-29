import React from "react";
import { Globe, Home, Truck, Package, DollarSign, Compass } from "lucide-react";

export const MASTER_CATEGORIES = [
  {
    id: "geography",
    name: "Geography",
    icon: Globe,
    entities: [
      { id: "countries", name: "Countries", label: "Country" },
      { id: "states", name: "States", label: "State" },
      { id: "districts", name: "Districts", label: "District" },
      { id: "cities", name: "Cities", label: "City" },
      { id: "destinations", name: "Destinations", label: "Destination" },
    ],
  },
  {
    id: "accommodation",
    name: "Accommodation",
    icon: Home,
    entities: [
      { id: "hotel-categories", name: "Hotel Categories", label: "Hotel Category" },
      { id: "meal-plans", name: "Meal Plans", label: "Meal Plan" },
      { id: "seasons", name: "Seasons", label: "Season" },
    ],
  },
  {
    id: "transport",
    name: "Transport",
    icon: Truck,
    entities: [
      { id: "vehicle-types", name: "Vehicle Types", label: "Vehicle Type" },
    ],
  },
  {
    id: "activities",
    name: "Activities",
    icon: Compass,
    entities: [
      { id: "activity-types", name: "Activity Types", label: "Activity Type" },
    ],
  },
  {
    id: "packages",
    name: "Packages",
    icon: Package,
    entities: [
      { id: "package-categories", name: "Package Categories", label: "Package Category" },
      { id: "cancellation-policies", name: "Cancellation Policies", label: "Cancellation Policy" },
    ],
  },
  {
    id: "finance",
    name: "Finance",
    icon: DollarSign,
    entities: [
      { id: "currencies", name: "Currencies", label: "Currency" },
      { id: "payment-methods", name: "Payment Methods", label: "Payment Method" },
      { id: "tax-configurations", name: "Tax Configurations", label: "Tax Configuration" },
    ],
  },
];

export function MasterTabs({
  activeCategoryId,
  onCategoryChange,
  activeEntitySlug,
  onEntityChange,
}) {
  const activeCategory = MASTER_CATEGORIES.find((c) => c.id === activeCategoryId) || MASTER_CATEGORIES[0];

  return (
    <div className="space-y-3 shrink-0 select-none">
      {/* Category Tabs Header */}
      <div className="flex border-b border-slate-200 bg-white rounded-xl overflow-hidden shadow-sm border">
        {MASTER_CATEGORIES.map((category) => {
          const Icon = category.icon;
          const isActive = activeCategoryId === category.id;
          return (
            <button
              key={category.id}
              onClick={() => {
                onCategoryChange(category.id);
                onEntityChange(category.entities[0].id);
              }}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 border-b-2 text-xs font-bold transition-all focus:outline-none ${
                isActive
                  ? "border-blue-600 text-blue-600 bg-blue-50/30"
                  : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50"
              }`}
            >
              <Icon size={16} />
              <span>{category.name}</span>
            </button>
          );
        })}
      </div>

      {/* Sub-selector Pills */}
      <div className="flex items-center space-x-2 flex-wrap gap-1.5 pt-1">
        {activeCategory.entities.map((entity) => {
          const isActive = activeEntitySlug === entity.id;
          return (
            <button
              key={entity.id}
              onClick={() => onEntityChange(entity.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all focus:outline-none ${
                isActive
                  ? "bg-slate-800 text-white shadow-sm"
                  : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              {entity.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default MasterTabs;
