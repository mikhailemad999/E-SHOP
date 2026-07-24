import { create } from 'zustand';

export const useCartStore = create((set, get) => ({
  items: [],
  addItem: (item) => {
    const current = get().items;
    const existingIndex = current.findIndex((i) => i.listing_id === item.listing_id);
    if (existingIndex > -1) {
      const updated = [...current];
      updated[existingIndex].quantity += item.quantity || 1;
      set({ items: updated });
    } else {
      set({ items: [...current, { ...item, quantity: item.quantity || 1 }] });
    }
  },
  removeItem: (listing_id) => {
    set({ items: get().items.filter((i) => i.listing_id !== listing_id) });
  },
  clearCart: () => set({ items: [] }),
  getTotalPrice: () => get().items.reduce((total, i) => total + i.price * i.quantity, 0),
  getItemCount: () => get().items.reduce((count, i) => count + i.quantity, 0),
}));
