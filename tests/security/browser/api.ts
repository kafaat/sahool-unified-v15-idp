// Supplied fields must avoid the network API; the map renderer itself is real.
export const apiClient = {
  getFields() { throw new Error('The supplied-field map must not fetch API data'); },
};
